# -*- coding: utf-8 -*-

from gettext import bindtextdomain, dgettext, gettext
from os import environ

from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, resolveFilename


def localeInit():
	lang = language.getLanguage()[:2]
	environ["LANGUAGE"] = lang
	bindtextdomain("PluginHider", resolveFilename(SCOPE_PLUGINS, "Extensions/PluginHider/locale"))


def _(txt):
	t = dgettext("PluginHider", txt)
	if t == txt:
		t = gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
