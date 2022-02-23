import hid
import struct
import time

class LenovoKeyboardBacklight:
    def __init__(self):
        self.dev = hid.device()

    def __enter__(self):
        dev_desc = next(desc for desc in hid.enumerate(vendor_id=0x048d) if desc['product_id'] in [ 0xc965, 0xc955 ])
        self.dev.open(dev_desc['vendor_id'], dev_desc['product_id'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.close()

    def get_current_profile(self):
        return self.dev.get_feature_report(0xcc, 32)[1]

    def wait_for_profile_change(self):
        old_profile = self.get_current_profile()
        for i in range(100):
            new_profile = self.get_current_profile()
            if new_profile != old_profile:
                return new_profile
            time.sleep(0.01)
        return old_profile

    def set_solid(self, colors, brightness, pulse_speed = 0):
        self.set_internal(colors, 1 if pulse_speed == 0 else 3, brightness, pulse_speed, [ 0, 0, 0 ])

    def set_wave_effect(self, brightness, speed, left_to_right):
        wave_type = [ 0, 0, 1] if left_to_right else [ 0, 1, 0 ]
        self.set_internal([ 0, 0, 0, 0 ], 4, brightness, speed, wave_type)

    def set_color_fade(self, brightness, speed):
        self.set_internal([ 0, 0, 0, 0 ], 6, brightness, speed, [ 0, 0, 0 ])

    def set_internal(self, colors, mode, brightness, speed, wave_type):
        is_now_off = self.get_current_profile() == 4

        if brightness == 0 and is_now_off:
            colors = [ 0 for i in range(4) ]
        colorbytes = list(map(lambda c: (c if isinstance(c, int) else int(c, 0)).to_bytes(3, 'big'), colors))

        if brightness == 0:
            mode = 0

        report = struct.pack('BBBBB3s3s3s3s3x3s10x', 204, 22, int(mode), speed, brightness, colorbytes[0], colorbytes[1], colorbytes[2], colorbytes[3], bytes(wave_type))
        self.dev.send_feature_report(report)
