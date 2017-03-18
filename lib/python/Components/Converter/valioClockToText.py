from Converter import Converter
from time import localtime, strftime
from Components.Element import cached



class valioClockToText(Converter, object):
	DEFAULT = 0
	WITH_SECONDS = 1
	IN_MINUTES = 2
	DATE = 3
	FORMAT = 4
	AS_LENGTH = 5
	TIMESTAMP = 6
	ONLYDATE = 7
	DATETIME = 8
	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "WithSeconds":
			self.type = self.WITH_SECONDS
		elif type == "InMinutes":
			self.type = self.IN_MINUTES
		elif type == "Date":
			self.type = self.DATE
		elif type == "OnlyDate":
			self.type = self.ONLYDATE
		elif type == "DateTime":
			self.type = self.DATETIME
		elif type == "AsLength":
			self.type = self.AS_LENGTH
		elif type == "Timestamp":	
			self.type = self.TIMESTAMP
		elif str(type).find("Format") != -1:
			self.type = self.FORMAT
			self.fmt_string = type[7:]
		else:
			self.type = self.DEFAULT

	@cached
	def getText(self):
		time = self.source.time
		if time is None:
			return ""
		if self.type == self.IN_MINUTES:
			return "%d min" % (time / 60)
		elif self.type == self.AS_LENGTH:
			return "%d:%02d" % (time / 60, time % 60)
		elif self.type == self.TIMESTAMP:
			return str(time)
		t = localtime(time)
		if self.type == self.WITH_SECONDS:
			return "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
		elif self.type == self.DEFAULT:
			return "%02d:%02d" % (t.tm_hour, t.tm_min)
		elif self.type == self.DATE:
			tmpstr = strftime("%A %d %m", t)
			sepstr = tmpstr.split(" ")
			sepstr[0] = _(sepstr[0])
			return sepstr[0]+"-"+sepstr[1]+"-"+sepstr[2]
		elif self.type == self.DATETIME:
			tmpstr = strftime("%a %d %m %H:%M", t)
			sepstr = tmpstr.split(" ")
			sepstr[0] = _(sepstr[0])
			return sepstr[0]+"-"+sepstr[1]+"-"+sepstr[2]+"    "+sepstr[3]
		elif self.type == self.ONLYDATE:
			tmpstr = strftime("%a %d %m", t)
			sepstr = tmpstr.split(" ")
			sepstr[0] = _(sepstr[0])
			return sepstr[0]+"-"+sepstr[1]+"-"+sepstr[2]
		elif self.type == self.FORMAT:
			spos = self.fmt_string.find('%')
			if spos > 0:
				s1 = self.fmt_string[:spos]
				s2 = strftime(self.fmt_string[spos:], t)
				tmpstr = str(s1+s2)
			else:
				tmpstr = strftime(self.fmt_string, t)
			newstr = []
			sepstr = tmpstr.split(" ")
			for x in sepstr:
				if x.isalpha():
					x = _(x)
				newstr.append(x)
			return " ".join(newstr)
		else:
			return "???"

	text = property(getText)
