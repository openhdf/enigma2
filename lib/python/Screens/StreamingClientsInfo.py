from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Converter.ClientsStreaming import ClientsStreaming
from Components.config import config
from Components.Sources.StaticText import StaticText
from enigma import eTimer, eStreamServer
import skin


class StreamingClientsInfo(Screen):
	def __init__(self, session, menu_path = ""):
		Screen.__init__(self, session)
		self.timer = eTimer()
		screentitle = _("Streaming clients info")
		menu_path += screentitle
		if config.usage.show_menupath.value == 'large':
			title = menu_path
			self["menu_path_compressed"] = StaticText("")
		elif config.usage.show_menupath.value == 'small':
			title = screentitle
			self["menu_path_compressed"] = StaticText(menu_path + " >" if not menu_path.endswith(' / ') else menu_path[:-3] + " >" or "")
		else:
			title = screentitle
			self["menu_path_compressed"] = StaticText("")
		Screen.setTitle(self, title)

		self["ScrollLabel"] = ScrollLabel()
		self["ScrollLabel2"] = ScrollLabel()

		self["key_red"] = Button(_("Close"))
		self["key_blue"] = Button(_("Stop Streams"))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.exit,
				"ok": self.exit,
				"red": self.exit,
				"blue": self.stopStreams,
				"up": self["ScrollLabel"].pageUp,
				"down": self["ScrollLabel"].pageDown
			})

		self.onLayoutFinish.append(self.start)

	def exit(self):
		self.stop()
		self.close()

	def start(self):
		if self.update_info not in self.timer.callback:
			self.timer.callback.append(self.update_info)
		self.timer.startLongTimer(0)

	def stop(self):
		if self.update_info in self.timer.callback:
			self.timer.callback.remove(self.update_info)
		self.timer.stop()

	def update_info(self):
		clients = ClientsStreaming("SHORT_ALL")
		clients2 = ClientsStreaming("EXTRA_INFO")
		#clients3 = ClientsStreaming("SHORT_ALL")
		text = clients.getText()
		text2 = clients2.getText()
		self["ScrollLabel"].setText(text or _("Currently nothing is streamed to clients"))
		self["ScrollLabel2"].setText(text2 or _("Currently nothing is streamed to clients"))
		self["key_blue"].setText(text and _("Stop Streams") or "")
		self.timer.startLongTimer(5)

	def stopStreams(self):
		streamServer = eStreamServer.getInstance()
		if not streamServer:
			return
		for x in streamServer.getConnectedClients():
			streamServer.stopStream()
