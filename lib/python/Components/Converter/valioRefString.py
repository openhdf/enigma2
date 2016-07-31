#######################################################################
#
#    ReferenceToString for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2011
#
#######################################################################

from Components.Converter.Converter import Converter
from Components.Element import cached
from Screens.InfoBar import InfoBar

class valioRefString(Converter, object):
	CURRENT = 0
	EVENT = 1
	def __init__(self, type):
		Converter.__init__(self, type)
		self.CHANSEL = None
		self.type = {
				"CurrentRef": self.CURRENT,
				"ServicelistRef": self.EVENT
			}[type]

	@cached
	def getText(self):
		if (self.type == self.EVENT):
			antw = str(self.source.service.toString())
			if antw[:6] == "1:7:0:":
				teilantw = antw.split("ORDER BY name:")
				if len(teilantw)>1:
					teil2antw = teilantw[1].split()
					if len(teil2antw)>0:
						#print "#####Picon-170###################" + teil2antw[0]
						return teil2antw[0]
			elif antw[:6] == "1:7:1:":
				teilantw = antw.split(".")
				if len(teilantw)>1:
					#print "#####Picon-171###################" + teilantw[1]
					return teilantw[1]
			#print "#####Picon#######################" + antw
			return antw
		elif (self.type == self.CURRENT):
			if self.CHANSEL == None:
				self.CHANSEL = InfoBar.instance.servicelist
			if len(InfoBar.instance.session.dialog_stack)>1:
				#print "#####Screen#####" + str(InfoBar.instance.session.dialog_stack)
				for zz in InfoBar.instance.session.dialog_stack:
					if (str(zz[0]) == "<class 'Screens.MovieSelection.MovieSelection'>") or (str(InfoBar.instance.session.dialog_stack[1][0]) == "<class 'Screens.InfoBar.MoviePlayer'>"):
						#print "#####Picon-Movie#################" + self.source.text
						return self.source.text
						#return "movie"
			vSrv = self.CHANSEL.servicelist.getCurrent()
			#print "#####Picon#######################" + str(vSrv.toString())
			return str(vSrv.toString())
		else:
			return "na"

	text = property(getText)
