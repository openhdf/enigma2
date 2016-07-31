#######################################################################
#
#    Renderer CAID's for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2011
#
#######################################################################



from Renderer import Renderer
from enigma import eCanvas, eRect, gFont
from skin import parseColor, parseFont



class valioCAD(Renderer):
	GUI_WIDGET = eCanvas

	def __init__(self):
		Renderer.__init__(self)
		self.backgroundColor = parseColor("#ff000000")
		self.emmColor = parseColor("#00aaaaaa")
		self.clGrey = parseColor("#00aaaaaa")
		self.ecmColor = parseColor("#0056c856")
		self.font = gFont("Regular", 20)

	def pull_updates(self):
		if self.instance is None:
			return
		self.instance.clear(self.backgroundColor)
		caidlist,newtxt = self.source.getCaidlist
		if caidlist is None:
			return
		self.draw(caidlist, newtxt)

	def draw(self, caidlist, newtxt):
		offset = 0
		pointSize = self.font.pointSize
		for key in caidlist:
			if caidlist[key][0]:
				if caidlist[key][1] == 0:
					foregroundColor = self.emmColor
				else:
					foregroundColor = self.ecmColor
				length = len(caidlist[key][0]) * (pointSize )
				self.instance.writeText(eRect(offset, 0, length, pointSize), foregroundColor, self.backgroundColor, self.font, caidlist[key][0], 2)
				offset = offset + length
		foregroundColor = self.clGrey
		length = len(newtxt) * (pointSize )
		self.instance.writeText(eRect(offset, 0, length, pointSize), foregroundColor, self.backgroundColor, self.font, newtxt, 0)

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
			elif attrib == "emmColor":
				self.emmColor = parseColor(value)
			elif attrib == "ecmColor":
				self.ecmColor = parseColor(value)
			elif attrib == "fgColor":
				self.clGrey = parseColor(value)
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
