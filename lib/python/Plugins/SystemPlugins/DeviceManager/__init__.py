# -*- coding: utf-8 -*-
from __future__ import absolute_import
from gettext import dgettext, gettext

#def localeInit():
#	gettext.bindtextdomain("DeviceManager", resolveFilename(SCOPE_PLUGINS, "SystemPlugins/DeviceManager/locale"))


def _(txt):
	t = dgettext("DeviceManager", txt)
	if t == txt:
#		print "[DeviceManager] fallback to default translation for:", txt
		t = gettext(txt)
	return t

#localeInit()
#language.addCallback(localeInit)
