from __future__ import absolute_import
import sys
from enigma import ePythonOutput
import six


class EnigmaLog:
	def __init__(self, level):
		self.level = level
		self.line = ""

	def write(self, data):
		if sys.version_info[0] >= 3:
			if isinstance(data, bytes):
				data = six.ensure_str(data, errors="ignore")
		else:
			if isinstance(data, unicode):
				data = six.ensure_str(data, errors="ignore")
		self.line += data
		if "\n" in data:
			ePythonOutput(self.line, self.level)
			self.line = ""

	def flush(self):
		pass

	def isatty(self):
		return True


class EnigmaLogDebug(EnigmaLog):
	def __init__(self):
		EnigmaLog.__init__(self, 4)  # lvlDebug = 4


class EnigmaLogFatal(EnigmaLog):
	def __init__(self):
		EnigmaLog.__init__(self, 1)  # lvlError = 1


sys.stdout = EnigmaLogDebug()
sys.stderr = EnigmaLogFatal()
