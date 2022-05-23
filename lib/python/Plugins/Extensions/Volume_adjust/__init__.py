from __future__ import absolute_import
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE #@UnresolvedImport
from gettext import bindtextdomain, textdomain, bindtextdomain, dgettext, gettext
from os import environ

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
