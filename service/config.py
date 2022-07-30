import configobj

class Config:
    def __init__(self, filename):
        self.filename = filename
        self.config = None

    def __enter__(self):
        self.read_from_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read_from_file(self):
        new_config = configobj.ConfigObj(infile=self.filename)
        if self.config and self.config == new_config:
            return False
        self.config = new_config
        self.colorcfg = new_config.get('Color', {})
        self.brightnesscfg = new_config.get('Brightness', {})
        return True

    def colors(self):
        try:
            unicolor = self.colorcfg['SingleColorOnly'] == 'yes'
        except:
            unicolor = False
        return [ int(self.colorcfg.get(f'Color%d' % (1 if unicolor else (i + 1)), '0xffffff'), 0) for i in range(4) ]

    def brightness(self):
        return int(self.brightnesscfg.get('Current', '2'))

    def last_active_brightness(self):
        return int(self.brightnesscfg.get('LastOnValue', '2'))

    def set_brightness(self, brightness):
        if brightness > 0:
            self.brightnesscfg['LastOnValue'] = str(brightness)
        self.brightnesscfg['Current'] = str(brightness)
        self.config.write()

    def mode(self):
        return self.colorcfg.get('Mode', 'solid')

    def speed(self):
        if self.mode() in [ "pulse", "wave_left", "wave_right", "color_fade" ]:
            return int(self.colorcfg.get('Speed', '1'))
        return 0
