# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from os import environ
from gettext import gettext, bindtextdomain, dgettext


def localeInit():
	lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
	environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
	bindtextdomain("VirtualZap", resolveFilename(SCOPE_PLUGINS, "Extensions/VirtualZap/locale"))


def _(txt):
	t = dgettext("VirtualZap", txt)
	if t == txt:
		print("[VirtualZap] fallback to default translation for", txt)
		t = gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
