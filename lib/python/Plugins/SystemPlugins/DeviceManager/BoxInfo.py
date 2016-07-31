import os
import re

class BoxInfo:

    def __init__(self):
        self.isIPBOX = False
        self.isDMM = False
        self.scriptsPath = ''
        self.settingsMounts = ''
        self.settingsSwap = ''
        self.settingsModules = ''
        self.settingsHdparm = ''
        self.sfdiskBin = ''

    def detectBox(self):
        dmm_boxes = ['dm800', 'dm8000', 'dm500hd']
        f = open('/proc/stb/info/model', 'r')
        model = f.read().strip()
        try:
            dmm_boxes.index(model)
            self.isDMM = True
        except:
            self.isIPBOX = True

        f.close()
        if self.isDMM:
            self.scriptsPath = '/usr/script/'
            self.settingsMounts = '/etc/settings.mounts'
            self.settingsSwap = '/etc/settings.swap'
            self.settingsModules = '/etc/settings.modules'
            self.settingsHdparm = '/etc/settings.hdparm'
            self.sfdiskBin = '/usr/sbin/sfdisk'
        elif self.isIPBOX:
            self.scriptsPath = '/var/script/'
            self.settingsMounts = '/var/etc/settings.mounts'
            self.settingsSwap = '/var/etc/settings.swap'
            self.settingsModules = '/var/etc/settings.modules'
            self.settingsHdparm = '/var/etc/settings.hdparm'
            self.sfdiskBin = '/sbin/sfdisk'