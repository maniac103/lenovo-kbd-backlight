# lenovo-kbd-backlight

This is a daemon for controlling the 4-zone RGB backlight of the Lenovo Legion 5 Pro (2021) laptop when running in Linux.
It allows control over keyboard color effect (wave, pulse, solid etc.) as well as color (in pulse and solid modes; both
multi-zone and single-zone modes are supported). Brightness is advertised as LED device towards other applications, so the
keyboard brightness control is integrated into desktop environments.

## Installation

```
sudo python3 setup.py install --prefix=/usr/local
```
Then
- copy `lenovo-kbd-backlight.cfg` to `/etc`
- copy `lenovo-kbd-backlight.service` to a systemd service file directory (typically `/etc/systemd/system`)
- run `echo uleds | sudo tee /etc/modules-load.d/lenovo-kbd-backlight.conf` (to automatically load the `uleds` kernel module the service needs)
- run `sudo systemctl daemon-reload` to make systemd aware of the new file
- run `sudo systemctl enable lenovo-kbd-backlight` to enable the daemon

## Operation

As mentioned above, keyboard brightness is mapped to an LED file which should integrate keyboard brightness control into your
desktop environment, assuming the DE has support for that feature (it was successfully tested in KDE). Brightness control allows
for 3 brightness levels (off, dim, fully on). All other features, such as backlight color, need to be set via the config file and
should take effect immediately after saving the config file.
Please note the default keyboard brightness shortcut (Fn + space) works differently than in Windows: only one profile is supported,
so pressing Fn + space toggles between 'on' (using the last set brightness) and 'off' instead of moving between 4 profiles like it's
done in Windows.

