
from gettext import bindtextdomain, dgettext, gettext, textdomain
from os import environ

from Components.Language import language
from Tools.Directories import SCOPE_LANGUAGE  # @UnresolvedImport
from Tools.Directories import SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, resolveFilename

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
textdomain("enigma2")
bindtextdomain("Volume_adjust", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/Volume_adjust/locale/"))


def _(txt):
	t = dgettext("Volume_adjust", txt)
	if t == txt:
		t = gettext(txt)
	return t
