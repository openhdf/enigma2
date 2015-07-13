#
#  Caids - Renderer
#
#  Coded by Dr.Best (c) 2010
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from Renderer import Renderer
from enigma import eCanvas, eRect, gFont
from skin import parseColor, parseFont

class DMCHDCaids(Renderer):
	GUI_WIDGET = eCanvas

	def __init__(self):
		Renderer.__init__(self)
		self.backgroundColor = parseColor("#ff000000")
		self.nocColor = parseColor("#00aaaaaa")
		self.emmColor = parseColor("#00aaaaaa")
		self.ecmColor = parseColor("#0056c856")
		self.font = gFont("Regular", 20)

	def pull_updates(self):
		if self.instance is None:
			return
		self.instance.clear(self.backgroundColor)
		caidlist = self.source.getCaidlist
		if caidlist is None:
			return
		self.draw(caidlist)

	def draw(self, caidlist):
		offset = 0
		pointSize = self.font.pointSize
		for key in caidlist:
			if caidlist[key][0]:
				if caidlist[key][1] == 0:
				    foregroundColor = self.nocColor 					
				elif caidlist[key][1] == 1:
				    foregroundColor = self.emmColor
				else:
				    foregroundColor = self.ecmColor
				length = len(caidlist[key][0]) * (pointSize)
				self.instance.writeText(eRect(offset, 0, length, pointSize), foregroundColor, self.backgroundColor, self.font, caidlist[key][0], 2)
				offset = offset +  length

	def changed(self, what):
		self.pull_updates()

	def applySkin(self, desktop, parent):

		attribs = [ ]
		from enigma import eSize

		def parseSize(str):
			x, y = str.split(',')
			return eSize(int(x), int(y))

		for (attrib, value) in self.skinAttributes:
			if attrib == "size":
			    self.instance.setSize(parseSize(value))
			    attribs.append((attrib,value))
			elif attrib == "nocColor":
			    self.nocColor = parseColor(value)
			elif attrib == "emmColor":
			    self.emmColor = parseColor(value)
			elif attrib == "ecmColor":
			    self.ecmColor = parseColor(value)
			elif attrib == "font":
			    self.font = parseFont(value, ((1,1),(1,1)))
			elif attrib == "backgroundColor":
			    self.backgroundColor = parseColor(value)
			    self.instance.clear(self.backgroundColor)
			    attribs.append((attrib,value))
			else:
			    attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)
