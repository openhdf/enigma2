from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config
from Components.MenuList import MenuList
from Components.TimerList import TimerList
from Components.TimerSanityCheck import TimerSanityCheck
from Components.UsageConfig import preferredTimerPath
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.InputBox import PinInput
from ServiceReference import ServiceReference
from TimerEntry import TimerEntry, TimerLog
from Tools.BoundFunction import boundFunction
from time import time
from timer import TimerEntry as RealTimerEntry

class TimerEditList(Screen):
	EMPTY = 0
	ENABLE = 1
	DISABLE = 2
	CLEANUP = 3
	DELETE = 4

	def __init__(self, session):
		Screen.__init__(self, session)

		list = [ ]
		self.list = list
		self.fillTimerList()

		self["timerlist"] = TimerList(list)

		self.key_red_choice = self.EMPTY
		self.key_yellow_choice = self.EMPTY
		self.key_blue_choice = self.EMPTY

		self["key_red"] = Button(" ")
		self["key_green"] = Button(_("Add"))
		self["key_yellow"] = Button(" ")
		self["key_blue"] = Button(" ")

		print "[TimerEditList] key_red_choice:",self.key_red_choice

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ShortcutActions", "TimerEditActions"],
			{
				"ok": self.openEdit,
				"cancel": self.leave,
				"green": self.addCurrentTimer,
				"log": self.showLog,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down
			}, -1)
		self.setTitle(_("Timer overview"))
		# Disable for test because it crashes on some boxes with SSD #############
		#self.session.nav.RecordTimer.on_state_change.append(self.onStateChange)
		##########################################################################
		self.onShown.append(self.updateState)
		if self.isProtected() and config.ParentalControl.servicepin[0].value:
			self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList=[x.value for x in config.ParentalControl.servicepin], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code")))

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and (not config.ParentalControl.config_sections.main_menu.value or hasattr(self.session, 'infobar') and self.session.infobar is None) and config.ParentalControl.config_sections.timer_menu.value

	def pinEntered(self, result):
		if result is None:
			self.closeProtectedScreen()
		elif not result:
			self.session.openWithCallback(self.close(), MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR, timeout=3)

	def closeProtectedScreen(self, result=None):
		self.close(None)

	def up(self):
		self["timerlist"].instance.moveSelection(self["timerlist"].instance.moveUp)
		self.updateState()

	def down(self):
		self["timerlist"].instance.moveSelection(self["timerlist"].instance.moveDown)
		self.updateState()

	def left(self):
		self["timerlist"].instance.moveSelection(self["timerlist"].instance.pageUp)
		self.updateState()

	def right(self):
		self["timerlist"].instance.moveSelection(self["timerlist"].instance.pageDown)
		self.updateState()

	def toggleDisabledState(self):
		cur=self["timerlist"].getCurrent()
		timer_changed = True
		if cur:
			t = cur
			if t.disabled and t.repeated and t.isRunning() and not t.justplay:
				return
			if t.disabled:
				print "[TimerEditList] try to ENABLE timer"
				t.enable()
				timersanitycheck = TimerSanityCheck(self.session.nav.RecordTimer.timer_list, cur)
				if not timersanitycheck.check():
					t.disable()
					print "[TimerEditList] sanity check failed"
					simulTimerList = timersanitycheck.getSimulTimerList()
					if simulTimerList is not None:
						self.session.openWithCallback(self.finishedEdit, TimerSanityConflict, simulTimerList)
						timer_changed = False
				else:
					print "[TimerEditList] sanity check passed"
					if timersanitycheck.doubleCheck():
						t.disable()
			else:
				if t.isRunning():
					if t.repeated:
						list = (
							(_("Stop current event but not coming events"), "stoponlycurrent"),
							(_("Stop current event and disable coming events"), "stopall"),
							(_("Don't stop current event but disable coming events"), "stoponlycoming")
						)
						self.session.openWithCallback(boundFunction(self.runningEventCallback, t), ChoiceBox, title=_("Repeating event currently recording... What do you want to do?"), list = list)
						timer_changed = False
				else:
					t.disable()
			if timer_changed:
				self.session.nav.RecordTimer.timeChanged(t)
			self.refill()
			self.updateState()

	def runningEventCallback(self, t, result):
		if result is not None and t.isRunning():
			findNextRunningEvent = True
			if result[1] == "stoponlycurrent" or result[1] == "stopall":
				findNextRunningEvent = False
				t.enable()
				t.processRepeated(findRunningEvent = False)
				self.session.nav.RecordTimer.doActivate(t)
			if result[1] == "stoponlycoming" or result[1] == "stopall":
				findNextRunningEvent = True
				t.disable()
			self.session.nav.RecordTimer.timeChanged(t)
			t.findRunningEvent = findNextRunningEvent
			self.refill()
			self.updateState()

	def removeAction(self, descr):
		actions = self["actions"].actions
		if descr in actions:
			del actions[descr]

	def updateState(self):
		cur = self["timerlist"].getCurrent()
		if cur:
			if self.key_red_choice != self.DELETE:
				self["actions"].actions.update({"red":self.removeTimerQuestion})
				self["key_red"].setText(_("Delete"))
				self.key_red_choice = self.DELETE

			if cur.disabled and (self.key_yellow_choice != self.ENABLE):
				if cur.isRunning() and cur.repeated and not cur.justplay:
					self.removeAction("yellow")
					self["key_yellow"].setText(" ")
					self.key_yellow_choice = self.EMPTY
				else:
					self["actions"].actions.update({"yellow":self.toggleDisabledState})
					self["key_yellow"].setText(_("Enable"))
					self.key_yellow_choice = self.ENABLE
			elif cur.isRunning() and not cur.repeated and (self.key_yellow_choice != self.EMPTY):
				self.removeAction("yellow")
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
			elif (not cur.isRunning() or cur.repeated) and not cur.disabled and (self.key_yellow_choice != self.DISABLE):
				self["actions"].actions.update({"yellow":self.toggleDisabledState})
				self["key_yellow"].setText(_("Disable"))
				self.key_yellow_choice = self.DISABLE
		else:
			if self.key_red_choice != self.EMPTY:
				self.removeAction("red")
				self["key_red"].setText(" ")
				self.key_red_choice = self.EMPTY
			if self.key_yellow_choice != self.EMPTY:
				self.removeAction("yellow")
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY

		showCleanup = True
		for x in self.list:
			if (not x[0].disabled) and (x[1] == True):
				break
		else:
			showCleanup = False

		if showCleanup and (self.key_blue_choice != self.CLEANUP):
			self["actions"].actions.update({"blue":self.cleanupQuestion})
			self["key_blue"].setText(_("Cleanup"))
			self.key_blue_choice = self.CLEANUP
		elif (not showCleanup) and (self.key_blue_choice != self.EMPTY):
			self.removeAction("blue")
			self["key_blue"].setText(" ")
			self.key_blue_choice = self.EMPTY

	def fillTimerList(self):
		#helper function to move finished timers to end of list
		def eol_compare(x, y):
			if x[0].state != y[0].state and x[0].state == RealTimerEntry.StateEnded or y[0].state == RealTimerEntry.StateEnded:
				return cmp(x[0].state, y[0].state)
			return cmp(x[0].begin, y[0].begin)

		list = self.list
		del list[:]
		list.extend([(timer, False) for timer in self.session.nav.RecordTimer.timer_list])
		list.extend([(timer, True) for timer in self.session.nav.RecordTimer.processed_timers])
		if config.usage.timerlist_finished_timer_position.index: #end of list
			list.sort(cmp = eol_compare)
		else:
			list.sort(key = lambda x: x[0].begin)

	def showLog(self):
		cur=self["timerlist"].getCurrent()
		if cur:
			self.session.openWithCallback(self.finishedEdit, TimerLog, cur)

	def openEdit(self):
		cur=self["timerlist"].getCurrent()
		if cur:
			self.session.openWithCallback(self.finishedEdit, TimerEntry, cur)

	def cleanupQuestion(self):
		self.session.openWithCallback(self.cleanupTimer, MessageBox, _("Really delete done timers?"))

	def cleanupTimer(self, delete):
		if delete:
			self.session.nav.RecordTimer.cleanup()
			self.refill()
			self.updateState()

	def removeTimerQuestion(self):
		cur = self["timerlist"].getCurrent()
		if not cur:
			return

		self.session.openWithCallback(self.removeTimer, MessageBox, _("Do you really want to delete %s?") % (cur.name))

	def removeTimer(self, result):
		if not result:
			return
		list = self["timerlist"]
		cur = list.getCurrent()
		if cur:
			timer = cur
			timer.afterEvent = AFTEREVENT.NONE
			self.session.nav.RecordTimer.removeEntry(timer)
			self.refill()
			self.updateState()


	def refill(self):
		oldsize = len(self.list)
		self.fillTimerList()
		lst = self["timerlist"]
		newsize = len(self.list)
		if oldsize and oldsize != newsize:
			idx = lst.getCurrentIndex()
			lst.entryRemoved(idx)
		else:
			lst.invalidate()

	def addCurrentTimer(self):
		event = None
		service = self.session.nav.getCurrentService()
		if service is not None:
			info = service.info()
			if info is not None:
				event = info.getEvent(0)

		# FIXME only works if already playing a service
		serviceref = ServiceReference(self.session.nav.getCurrentlyPlayingServiceOrGroup())

		if event is None:
			data = (int(time()), int(time() + 60), "", "", None)
		else:
			data = parseEvent(event, description = False)

		self.addTimer(RecordTimerEntry(serviceref, checkOldTimers = True, dirname = preferredTimerPath(), *data))

	def addTimer(self, timer):
		self.session.openWithCallback(self.finishedAdd, TimerEntry, timer)


	def finishedEdit(self, answer):
		print "[TimerEditList] finished edit"

		if answer[0]:
			print "[TimerEditList] edited timer"
			entry = answer[1]
			timersanitycheck = TimerSanityCheck(self.session.nav.RecordTimer.timer_list, entry)
			success = False
			if not timersanitycheck.check():
				simulTimerList = timersanitycheck.getSimulTimerList()
				if simulTimerList is not None:
					for x in simulTimerList:
						if x.setAutoincreaseEnd(entry):
							self.session.nav.RecordTimer.timeChanged(x)
					if not timersanitycheck.check():
						simulTimerList = timersanitycheck.getSimulTimerList()
						if simulTimerList is not None:
							self.session.openWithCallback(self.finishedEdit, TimerSanityConflict, timersanitycheck.getSimulTimerList())
					else:
						success = True
			else:
				success = True
			if success:
				print "[TimerEditList] sanity check passed"
				self.session.nav.RecordTimer.timeChanged(entry)

			self.fillTimerList()
			self.updateState()
		else:
			print "[TimerEditList] timer edit aborted"

	def finishedAdd(self, answer):
		print "[TimerEditList] finished add"
		if answer[0]:
			entry = answer[1]
			simulTimerList = self.session.nav.RecordTimer.record(entry)
			if simulTimerList is not None:
				for x in simulTimerList:
					if x.setAutoincreaseEnd(entry):
						self.session.nav.RecordTimer.timeChanged(x)
				simulTimerList = self.session.nav.RecordTimer.record(entry)
				if simulTimerList is not None:
					self.session.openWithCallback(self.finishSanityCorrection, TimerSanityConflict, simulTimerList)
			self.fillTimerList()
			self.updateState()
		else:
			print "[TimerEditList] timer edit aborted"

	def finishSanityCorrection(self, answer):
		self.finishedAdd(answer)

	def leave(self):
		# Disable for test because it crashes on some boxes with SSD #############
		#self.session.nav.RecordTimer.on_state_change.remove(self.onStateChange)
		##########################################################################
		self.close()

	def onStateChange(self, entry):
		self.refill()
		self.updateState()

class TimerSanityConflict(Screen):
	EMPTY = 0
	ENABLE = 1
	DISABLE = 2
	EDIT = 3

	def __init__(self, session, timer):
		Screen.__init__(self, session)
		self.timer = timer
		print "[TimerSanityConflict] open window"

		self["timer1"] = TimerList(self.getTimerList(timer[0]))
		self.list = []
		self.list2 = []
		count = 0
		for x in timer:
			if count != 0:
				self.list.append((_("Conflicting timer") + " " + str(count), x))
				self.list2.append((timer[count], False))
			count += 1
		if count == 1:
			self.list.append((_("Channel not in services list")))

		self["list"] = MenuList(self.list)
		self["timer2"] = TimerList(self.list2)

		self["key_red"] = Button(_("Edit"))
		self["key_green"] = Button(" ")
		self["key_yellow"] = Button(" ")
		self["key_blue"] = Button(" ")

		self.key_green_choice = self.EMPTY
		self.key_yellow_choice = self.EMPTY
		self.key_blue_choice = self.EMPTY

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ShortcutActions", "TimerEditActions"],
			{
				"ok": self.leave_ok,
				"cancel": self.leave_cancel,
				"red": self.editTimer1,
				"up": self.up,
				"down": self.down
			}, -1)
		self.setTitle(_("Timer sanity error"))
		self.onShown.append(self.updateState)

	def getTimerList(self, timer):
		return [(timer, False)]

	def editTimer1(self):
		self.session.openWithCallback(self.finishedEdit, TimerEntry, self["timer1"].getCurrent())

	def toggleTimer1(self):
		time_changed = False
		if self.timer[0].disabled:
			self.timer[0].enable()
			time_changed = True
		elif not self.timer[0].isRunning():
			self.timer[0].disable()
			time_changed = True
		if time_changed:
			self.session.nav.RecordTimer.timeChanged(self.timer[0])
			self.leave_ok()

	def editTimer2(self):
		self.session.openWithCallback(self.finishedEdit, TimerEntry, self["timer2"].getCurrent())

	def toggleTimer2(self):
		time_changed = False
		timer2 = self["timer2"].getCurrent()
		if timer2 is not None:
			if timer2.disabled:
				timer2.enable()
				time_changed = True
			elif not timer2.isRunning():
				timer2.disable()
				time_changed = True
			if time_changed:
				self.session.nav.RecordTimer.timeChanged(timer2)
				self.leave_ok()

	def finishedEdit(self, answer=None):
		if answer is not None and len(answer) > 1 and answer[0] is True:
			self.leave_ok()

	def leave_ok(self):
		if self.isResolvedConflict():
			self.close((True, self.timer[0]))
		else:
			self.updateState()
			self.session.open(MessageBox, _("Conflict not resolved!"), MessageBox.TYPE_ERROR, timeout=3)

	def leave_cancel(self):
		isTimerSave = self.timer[0] in self.session.nav.RecordTimer.timer_list
		if self.isResolvedConflict() or not isTimerSave:
			self.close((False, self.timer[0]))
		else:
			timer_text = ""
			if not self.timer[0].isRunning():
				self.timer[0].disabled = True
				self.session.nav.RecordTimer.timeChanged(self.timer[0])
				timer_text = _("\nTimer '%s' disabled!") % self.timer[0].name
			self.session.openWithCallback(self.canceling, MessageBox, _("Conflict not resolved!") + timer_text, MessageBox.TYPE_INFO, timeout=3)

	def canceling(self, answer=None):
		self.close((False, self.timer[0]))

	def isResolvedConflict(self):
		timersanitycheck = TimerSanityCheck(self.session.nav.RecordTimer.timer_list, self.timer[0])
		success = False
		if not timersanitycheck.check():
			simulTimerList = timersanitycheck.getSimulTimerList()
			if simulTimerList is not None:
				for x in simulTimerList:
					if x.setAutoincreaseEnd(self.timer[0]):
						self.session.nav.RecordTimer.timeChanged(x)
				if timersanitycheck.check():
					success = True
		else:
			success = True
		return success

	def up(self):
		self["list"].instance.moveSelection(self["list"].instance.moveUp)
		self["timer2"].moveToIndex(self["list"].getSelectedIndex())

	def down(self):
		self["list"].instance.moveSelection(self["list"].instance.moveDown)
		self["timer2"].moveToIndex(self["list"].getSelectedIndex())

	def removeAction(self, descr):
		actions = self["actions"].actions
		if descr in actions:
			del actions[descr]

	def updateState(self):
		if self.timer[0] is not None:
			if self.timer[0].disabled and self.key_green_choice != self.ENABLE:
				self["actions"].actions.update({"green":self.toggleTimer1})
				self["key_green"].setText(_("Enable"))
				self.key_green_choice = self.ENABLE
			elif self.timer[0].isRunning() and not self.timer[0].repeated and self.key_green_choice != self.EMPTY:
				self.removeAction("green")
				self["key_green"].setText(" ")
				self.key_green_choice = self.EMPTY
			elif (not self.timer[0].isRunning() or self.timer[0].repeated ) and self.key_green_choice != self.DISABLE:
				self["actions"].actions.update({"green":self.toggleTimer1})
				self["key_green"].setText(_("Disable"))
				self.key_green_choice = self.DISABLE

		total = len(self.timer)
		timer2 = self["timer2"].getCurrent()
		if total > 1:
			if timer2 is not None:
				if self.key_yellow_choice == self.EMPTY:
					self["actions"].actions.update({"yellow":self.editTimer2})
					self["key_yellow"].setText(_("Edit"))
					self.key_yellow_choice = self.EDIT
				if timer2.disabled and self.key_blue_choice != self.ENABLE:
					self["actions"].actions.update({"blue":self.toggleTimer2})
					self["key_blue"].setText(_("Enable"))
					self.key_blue_choice = self.ENABLE
				elif timer2.isRunning() and not timer2.repeated and self.key_blue_choice != self.EMPTY:
					self.removeAction("blue")
					self["key_blue"].setText(" ")
					self.key_blue_choice = self.EMPTY
				elif (not timer2.isRunning() or timer2.repeated) and self.key_blue_choice != self.DISABLE:
					self["actions"].actions.update({"blue":self.toggleTimer2})
					self["key_blue"].setText(_("Disable"))
					self.key_blue_choice = self.DISABLE
		if total < 2 or timer2 is None:
			if self.key_yellow_choice != self.EMPTY:
				self.removeAction("yellow")
				self["key_yellow"].setText(" ")
				self.key_yellow_choice = self.EMPTY
			if self.key_blue_choice != self.EMPTY:
				self.removeAction("blue")
				self["key_blue"].setText(" ")
				self.key_blue_choice = self.EMPTY
