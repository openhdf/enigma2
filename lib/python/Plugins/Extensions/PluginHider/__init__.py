# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from os import environ as os_environ
import gettext


def localeInit():
	lang = language.getLanguage()[:2]
	os_environ["LANGUAGE"] = lang
	gettext.bindtextdomain("PluginHider", resolveFilename(SCOPE_PLUGINS, "Extensions/PluginHider/locale"))


def _(txt):
	t = gettext.dgettext("PluginHider", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
