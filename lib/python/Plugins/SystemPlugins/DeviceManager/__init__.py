# -*- coding: utf-8 -*-
from __future__ import absolute_import
import gettext

#def localeInit():
#	gettext.bindtextdomain("DeviceManager", resolveFilename(SCOPE_PLUGINS, "SystemPlugins/DeviceManager/locale"))


def _(txt):
	t = gettext.dgettext("DeviceManager", txt)
	if t == txt:
#		print "[DeviceManager] fallback to default translation for:", txt
		t = gettext.gettext(txt)
	return t

#localeInit()
#language.addCallback(localeInit)
