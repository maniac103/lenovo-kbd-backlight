#!/usr/bin/env python3

import select
import struct
import sys
import systemd.daemon
from .config import Config
from .kbd_bl_api import LenovoKeyboardBacklight
from inotify_simple import INotify, flags
from pyroute2.netlink.event.acpi_event import AcpiEventSocket

def update_brightness(config):
    with open('/sys/class/leds/kbd_backlight/brightness', 'w') as brt:
        brt.write(str(config.brightness()))

def update_backlight(dev, config):
    brightness = config.brightness()
    speed = config.speed()
    mode = config.mode()

    if mode == 'wave_left':
        dev.set_wave_effect(brightness, speed, True)
    elif mode == 'wave_right':
        dev.set_wave_effect(brightness, speed, False)
    elif mode == 'color_fade':
        dev.set_color_fade(brightness, speed)
    else:
        dev.set_solid(config.colors(), brightness, speed)

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [configfile]" % sys.argv[0])
        sys.exit(1)

    with AcpiEventSocket() as acpi_source, Config(sys.argv[1]) as config, LenovoKeyboardBacklight() as backlight, open('/dev/uleds', 'rb+', 0) as led, INotify() as inotify:
        # create the leds class device
        led.write(struct.pack('64si', str.encode('kbd_backlight'), 2))

        update_brightness(config)
        update_backlight(backlight, config)

        systemd.daemon.notify('READY=1')
        inotify.add_watch(sys.argv[1], flags.MODIFY)

        p = select.epoll()
        p.register(acpi_source.fileno(), select.EPOLLIN)
        p.register(led.fileno(), select.EPOLLIN)
        p.register(inotify.fileno(), select.EPOLLIN)

        while True:
            for fileno, event in p.poll():
                if fileno == led.fileno():
                    b = struct.unpack('i', led.read(struct.calcsize('i')))[0]
                    config.set_brightness(b)
                    update_backlight(backlight, config)
                elif fileno == acpi_source.fileno():
                    for msg in acpi_source.get():
                        event = msg.get_attr('ACPI_GENL_ATTR_EVENT')
                        if event and event['bus_id'] == b'PNP0C14:01' and event['type'] == 58880:
                            profile = backlight.wait_for_profile_change()
                            new_brightness = 0 if profile == 4 else config.last_active_brightness()
                            config.set_brightness(new_brightness)
                            update_brightness(config) # will cause update_backlight
                            break
                elif fileno == inotify.fileno():
                    inotify.read() # clear POLLIN
                    if config.read_from_file():
                        update_brightness(config)
                        update_backlight(backlight, config)

