from Screens.Screen import Screen
from Components.Label import Label

class ShowPressedButtons(Screen):
	skin = """<screen position="center,0" size="300,50">
	<widget name="ShowPressedButton" position="center,center" size="200,50" font="Regular;20" color="white" />
	</screen>
	"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self["ShowPressedButton"] = Label()

	def setButton(self, key):
		print key
		self["ShowPressedButton"].setText(str(key))
