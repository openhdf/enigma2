from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2]
    os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain('SoftcamSetup', resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftcamSetup/locale'))

def _(txt):
    t = gettext.dgettext('SoftcamSetup', txt)
    if t == txt:
        print('[SoftcamSetup] fallback to default translation for', txt)
        t = gettext.gettext(txt)
    return t
localeInit()
language.addCallback(localeInit)
