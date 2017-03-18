from __init__ import _
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from UserDialog import UserDialog
from os import unlink, listdir, path as os_path

class UserManager(Screen):
    skin = '\n\t\t<screen name="UserManager" position="center,center" size="560,400" title="UserManager">\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t\t<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t\t<widget source="config" render="Listbox" position="5,50" size="540,220" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (80, 5), size = (400, 50), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (48, 48), png = 3), # index 4 is the status pixmap\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 40)],\n\t\t\t\t\t"itemHeight": 50\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<ePixmap pixmap="skin_default/div-h.png" position="0,360" zPosition="1" size="560,2" />\n\t\t\t<widget source="introduction" render="Label" position="10,370" size="540,21" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n\t\t</screen>'

    def __init__(self, session, plugin_path):
        self.skin_path = plugin_path
        self.session = session
        Screen.__init__(self, session)
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions'], {'ok': self.keyOK,
         'back': self.exit,
         'cancel': self.exit,
         'red': self.exit,
         'yellow': self.delete})
        self['key_red'] = StaticText(_('Close'))
        self['introduction'] = StaticText(_('Press OK to edit selected settings.'))
        self['key_yellow'] = StaticText(_('Delete'))
        self.list = []
        self['config'] = List(self.list)
        self.updateList()
        self.onShown.append(self.setWindowTitle)



    def setWindowTitle(self):
        self.setTitle(_('Usermanager'))



    def updateList(self):
        self.list = []
        for file in listdir('/etc/enigma2'):
            if file.endswith('.cache'):
                if file == 'networkbrowser.cache':
                    continue
                else:
                    hostpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/icons/host.png'))
                    self.list.append((file[:-6],
                     'edit',
                     file,
                     hostpng))

        self['config'].setList(self.list)



    def exit(self):
        self.close()



    def keyOK(self, returnValue = None):
        cur = self['config'].getCurrent()
        if cur:
            returnValue = cur[1]
            hostinfo = cur[0]
            if returnValue is 'edit':
                self.session.open(UserDialog, self.skin_path, hostinfo)



    def delete(self, returnValue = None):
        cur = self['config'].getCurrent()
        if cur:
            returnValue = cur[2]
            cachefile = '/etc/enigma2/' + returnValue.strip()
            if os_path.exists(cachefile):
                unlink(cachefile)
                self.updateList()
