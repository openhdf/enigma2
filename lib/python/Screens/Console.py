from __future__ import print_function
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Components.Label import Label
from six import ensure_str


class Console(Screen):
	def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False):
		Screen.__init__(self, session)

		self.finishedCallback = finishedCallback
		self.closeOnSuccess = closeOnSuccess
		self.errorOcurred = False

		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("hide"))

		self["text"] = ScrollLabel("")
		self["summary_description"] = StaticText("")
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
		{
			"ok": self.cancel,
			"back": self.cancel,
			"up": self.key_up,
			"down": self.key_down,
			"red": self.key_red,
			"yellow": self.key_yellow
		}, -1)

		self.cmdlist = cmdlist
		self.newtitle = title

		self.screen_hide = False
		self.cancel_msg = None

		self.onShown.append(self.updateTitle)

		self.container = eConsoleAppContainer()
		self.run = 0
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

	def updateTitle(self):
		self.setTitle(self.newtitle)

	def doExec(self, cmd):
		if isinstance(cmd, (list, tuple)):
			return self.container.execute(cmd[0], *cmd)
		else:
			return self.container.execute(cmd)

	def startRun(self):
		self["text"].setText(_("Start Execution:") + "\n\n")
		self["summary_description"].setText(_("Execution:"))
		print("[Console] executing in run", self.run, " the command:", self.cmdlist[self.run])
		if self.doExec(self.cmdlist[self.run]): #start of container application failed...
			self.runFinished(-1) # so we must call runFinished manual

	def runFinished(self, retval):
		if retval:
			self.errorOcurred = True
			self.toggleScreenHide(True)
		self.run += 1
		if self.run != len(self.cmdlist):
			if self.doExec(self.cmdlist[self.run]): #start of container application failed...
				self.runFinished(-1) # so we must call runFinished manual
		else:
			self["key_red"].setText(_("Close"))
			self["key_yellow"].setText(_(" "))
			self.toggleScreenHide(True)
			if self.cancel_msg:
				self.cancel_msg.close()
			lastpage = self["text"].isAtLastPage()
			self["text"].appendText(_("\nExecution finished!!"))
			self["summary_description"].setText(_("\nExecution finished!!"))
			if self.finishedCallback is not None:
				self.finishedCallback()
			if not self.errorOcurred and self.closeOnSuccess:
				self.cancel()

	def key_up(self):
		if self.screen_hide:
			self.toggleScreenHide()
			return
		self["text"].pageUp()

	def key_down(self):
		if self.screen_hide:
			self.toggleScreenHide()
			return
		self["text"].pageDown()

	def key_red(self):
		if self.screen_hide:
			self.toggleScreenHide()
			return
		if self.run == len(self.cmdlist):
			self.cancel(True)
		else:
			self.cancel_msg = self.session.openWithCallback(self.cancelCB, MessageBox, _("Really abort execution?"), type=MessageBox.TYPE_YESNO, default=False)

	def key_yellow(self):
		if self.screen_hide:
			self.toggleScreenHide()
			return
		else:
			if self.run != len(self.cmdlist):
				self.toggleScreenHide()

	def toggleScreenHide(self, setshow=False):
		if self.screen_hide or setshow:
			self.show()
		else:
			self.hide()
		self.screen_hide = not (self.screen_hide or setshow)

	def cancel(self, force=False):
		if self.screen_hide:
			self.toggleScreenHide()
			return
		if force or self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)
			if self.run != len(self.cmdlist):
				self.container.kill()

	def cancelCB(self, ret=None):
		self.cancel_msg = None
		if ret:
			self.cancel(True)

	def dataAvail(self, str):
		str = ensure_str(str)
		self["text"].appendText(str)
