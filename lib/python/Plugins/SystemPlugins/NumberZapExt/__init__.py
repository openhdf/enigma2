# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from os import environ
import os
import gettext

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("NumberZapExt", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/NumberZapExt/locale/"))

def _(txt):
	t = gettext.dgettext("NumberZapExt", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t