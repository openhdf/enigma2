
from os import path as os_path

from enigma import eTimer

from Components.config import config
from Components.Task import Job, Task
from Tools.Directories import fileExists


class CopyTimeshiftJob(Job):
	def __init__(self, toolbox, cmdline, srcfile, destfile, eventname):
		Job.__init__(self, _("Saving Timeshift files"))
		self.toolbox = toolbox
		AddCopyTimeshiftTask(self, cmdline, srcfile, destfile, eventname)


class AddCopyTimeshiftTask(Task):
	def __init__(self, job, cmdline, srcfile, destfile, eventname):
		Task.__init__(self, job, eventname)
		self.toolbox = job.toolbox
		self.setCmdline(cmdline)
		self.srcfile = config.usage.timeshift_path.value + srcfile + ".copy"
		self.destfile = destfile + ".ts"

		self.ProgressTimer = eTimer()
		self.ProgressTimer.callback.append(self.ProgressUpdate)

	def ProgressUpdate(self):
		if self.srcsize <= 0 or not fileExists(self.destfile, 'r'):
			return

		self.setProgress(int((os_path.getsize(self.destfile) / float(self.srcsize)) * 100))
		self.ProgressTimer.start(15000, True)

	def prepare(self):
		if fileExists(self.srcfile, 'r'):
			self.srcsize = os_path.getsize(self.srcfile)
			self.ProgressTimer.start(15000, True)

		self.toolbox.ptsFrontpanelActions("start")

	def afterRun(self):
		self.setProgress(100)
		self.ProgressTimer.stop()
		self.toolbox.ptsCopyFilefinished(self.srcfile, self.destfile)
		config.timeshift.isRecording.value = True


class MergeTimeshiftJob(Job):
	def __init__(self, toolbox, cmdline, srcfile, destfile, eventname):
		Job.__init__(self, _("Merging Timeshift files"))
		self.toolbox = toolbox
		AddMergeTimeshiftTask(self, cmdline, srcfile, destfile, eventname)


class AddMergeTimeshiftTask(Task):
	def __init__(self, job, cmdline, srcfile, destfile, eventname):
		Task.__init__(self, job, eventname)
		self.toolbox = job.toolbox
		self.setCmdline(cmdline)
		self.srcfile = config.usage.autorecord_path.value + srcfile
		self.destfile = config.usage.autorecord_path.value + destfile

		self.ProgressTimer = eTimer()
		self.ProgressTimer.callback.append(self.ProgressUpdate)

	def ProgressUpdate(self):
		if self.srcsize <= 0 or not fileExists(self.destfile, 'r'):
			return

		self.setProgress(int((os_path.getsize(self.destfile) / float(self.srcsize)) * 100))
		self.ProgressTimer.start(7500, True)

	def prepare(self):
		if fileExists(self.srcfile, 'r') and fileExists(self.destfile, 'r'):
			fsize1 = os_path.getsize(self.srcfile)
			fsize2 = os_path.getsize(self.destfile)
			self.srcsize = fsize1 + fsize2
			self.ProgressTimer.start(7500, True)

		self.toolbox.ptsFrontpanelActions("start")

	def afterRun(self):
		self.setProgress(100)
		self.ProgressTimer.stop()
		config.timeshift.isRecording.value = True
		self.toolbox.ptsMergeFilefinished(self.srcfile, self.destfile)


class CreateAPSCFilesJob(Job):
	def __init__(self, toolbox, cmdline, eventname):
		Job.__init__(self, _("Creating AP and SC Files"))
		self.toolbox = toolbox
		CreateAPSCFilesTask(self, cmdline, eventname)


class CreateAPSCFilesTask(Task):
	def __init__(self, job, cmdline, eventname):
		Task.__init__(self, job, eventname)
		self.toolbox = job.toolbox
		self.setCmdline(cmdline)

	def prepare(self):
		self.toolbox.ptsFrontpanelActions("start")
		config.timeshift.isRecording.value = True

	def afterRun(self):
		self.setProgress(100)
		self.toolbox.ptsSaveTimeshiftFinished()
