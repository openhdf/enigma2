from __future__ import absolute_import

from sys import stderr, stdout, version_info

from enigma import ePythonOutput
from six import ensure_str


class EnigmaLog:
	def __init__(self, level):
		self.level = level
		self.line = ""

	def write(self, data):
		if version_info[0] >= 3:
			if isinstance(data, bytes):
				data = ensure_str(data, errors="ignore")
		else:
			if isinstance(data, unicode):
				data = ensure_str(data, errors="ignore")
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


stdout = EnigmaLogDebug()
stderr = EnigmaLogFatal()
