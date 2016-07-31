#######################################################################
#
#    Channel Selection Tittle Renderer for Dreambox/Enigma-2
#    Version: 1.0
#    Coded by Vali (c)2010
#
#######################################################################



from Components.VariableText import VariableText
from Renderer import Renderer
from enigma import eLabel



class valioChSelTitle(VariableText, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			self.text = ""
		else:
			self.text = self.source.text.replace('Channel Selection (', '(')
