# -*- coding: utf-8 -*-
# by digiteng...12-2019

from __future__ import print_function
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, loadJPG
from Components.UsageConfig import *
import os
import re

posterpath = '/media/hdd/'
posterpath = config.usage.posterpath.value

if not posterpath:
	posterpath = "/media/hdd/"
print("posterpath:", posterpath)


class pstrRndr(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.pstrNm = ''
		self.path = ""

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == 'path':
				self.path = value
				if value.endswith("/"):
					self.path = value
				else:
					self.path = value + "/"
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap
	def changed(self, what):

		try:
			eventName = self.source.text
			if eventName:
				posterNm = re.sub('\s+', '+', eventName)
				pstrNm = posterpath + self.path + posterNm + ".jpg"

				if os.path.exists(pstrNm):
					self.instance.setPixmap(loadJPG(pstrNm))
					self.instance.show()
				else:
					self.instance.hide()
			else:
				self.instance.hide()
		except:
			pass
