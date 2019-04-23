from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox

class Console(Screen):
	def __init__(self, session, title = "Console", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
		Screen.__init__(self, session)

		self.finishedCallback = finishedCallback
		self.closeOnSuccess = closeOnSuccess
		self.errorOcurred = False
		self.hideflag = True

		self.Shown = True
		self["text"] = ScrollLabel("")
		self["summary_description"] = StaticText("")
		self["actions"] = ActionMap(["ColorActions", "WizardActions", "DirectionActions"],
		{
			"ok": self.ok,
			"back": self.cancel,
			"up": self["text"].pageUp,
			"down": self["text"].pageDown,
			"yellow": self.yellow
		}, -2)

		self.cmdlist = cmdlist
		self.newtitle = title
		self.cancel_cnt = 0
		self.cancel_msg = None
		self.onShown.append(self.updateTitle)

		self.container = eConsoleAppContainer()
		self.run = 0
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

	def updateTitle(self):
		self.setTitle(self.newtitle)

	def startRun(self):
		self["text"].setText(_("Start Execution:") + "\n\n")
		self["summary_description"].setText(_("Execution:"))
		print "Console: executing in run", self.run, " the command:", self.cmdlist[self.run]
		if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
			self.runFinished(-1) # so we must call runFinished manual

	def runFinished(self, retval):
		if retval:
			self.errorOcurred = True
		self.run += 1
		if self.run != len(self.cmdlist):
			if self.doExec(self.cmdlist[self.run]): #start of container application failed...
				self.runFinished(-1) # so we must call runFinished manual
		else:
			if self.cancel_msg:
				self.cancel_msg.close()
			lastpage = self["text"].isAtLastPage()
			self["text"].appendText('\n' + _("Execution finished!!"))
			self["summary_description"].setText('\n' + _("Execution finished!!"))
			if self.finishedCallback is not None:
				self.finishedCallback()
			if not self.errorOcurred and self.closeOnSuccess:
				self.cancel()

	def hideScreen(self):
		if self.hideflag == True:
			self.hideflag = False
			count = 40
			while count > 0:
				count -= 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (255 * count / 40))
				f.close()

		else:
			self.hideflag = True
			count = 0
			while count < 40:
				count += 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (255 * count / 40))
				f.close()

	def yellow(self):
		print 'Yellow Pressed'
		if self.Shown == True:
			self.hideScreen()
			self.Shown = False
		else:
			self.show()
			self.Shown = True

	def ok(self):
		if self.run == len(self.cmdlist):
			self.cancel()

	def cancel(self, force = False):
		if self.cancel_msg is not None:
			self.cancel_cnt = 0
			self.cancel_msg = None
			if not force:
				return
		self.cancel_cnt += 1
		if force or self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)
			if self.run != len(self.cmdlist):
				self.container.kill()
		elif self.cancel_cnt >= 3:
			self.cancel_msg = self.session.openWithCallback(self.cancel, MessageBox, _("Cancel the Script?"), type=MessageBox.TYPE_YESNO, default=False)
			self.cancel_msg.show()

	def dataAvail(self, str):
		lastpage = self["text"].isAtLastPage()
		self["text"].setText(self["text"].getText() + str)
		if lastpage:
			self["text"].lastPage()
