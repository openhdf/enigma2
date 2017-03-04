from six.moves.cPickle import load
import six
import enigma
with open(enigma.eEnv.resolve("${datadir}/enigma2/iso-639-3.pck"), 'rb') as f:
	LanguageCodes = load(f)


class ISO639Language:
	[PRIMARY, SECONDARY, TERTIARY] = [1, 2, 3]

	def __init__(self, depth=PRIMARY):
		self.depth = depth

		wanted_languages = []
		if depth == self.PRIMARY:
			wanted_languages = ["Undetermined", "English", "German", "Arabic", "Catalan", "Croatian", "Czech", "Danish", "Dutch", "Estonian", "Finnish", "French", "Greek", "Hungarian", "Lithuanian", "Latvian", "Icelandic", "Italian", "Norwegian", "Polish", "Portuguese", "Russian", "Serbian", "Slovakian", "Slovenian", "Spanish", "Swedish", "Turkish", "Ukrainian"]
		elif depth == self.SECONDARY:
			for key, val in six.iteritems(LanguageCodes):
				if len(key) == 2:
					wanted_languages.append(val[0])
		else:
			for key, val in six.iteritems(LanguageCodes):
				if len(key) == 3:
					wanted_languages.append(val[0])

		self.idlist_by_name = {}
		for key, val in six.iteritems(LanguageCodes):
			val = val[0]
			if val not in wanted_languages:
				continue
			if val not in self.idlist_by_name:
				self.idlist_by_name[val] = [key]
			else:
				self.idlist_by_name[val].append(key)

		self.name_and_shortid_by_longid = {}
		self.name_by_shortid = {}
		for lang, id_list in six.iteritems(self.idlist_by_name):
			long_ids = []
			short_id = None
			for id in id_list:
				if len(id) == 3:
					long_ids.append(id)
				if len(id) == 2:
					self.name_by_shortid[id] = lang
					short_id = id
			for long_id in long_ids:
				self.name_and_shortid_by_longid[long_id] = (short_id, lang)

	def getChoices(self):
		from Components.Language import language as syslanguage
		syslang = syslanguage.getLanguage()[:2]
		choices = []
		for lang, id_list in six.iteritems(self.idlist_by_name):
			if syslang not in id_list and 'en' not in id_list:
				choices.append((lang, lang))
		sorted(choices)
		choices.insert(0, (self.name_by_shortid[syslang], self.name_by_shortid[syslang]))
		if syslang != "en":
			choices.insert(1, (self.name_by_shortid["en"], self.name_by_shortid["en"]))
		return choices

	def determineLanguage(self, string):
		string = string.lower()
		language = "Undetermined"
		for word in ("stereo", "audio", "description", "2ch", "dolby digital", "2.0"):
			string = string.replace(word, "").strip()
		if len(string) == 2 and string in self.name_by_shortid:
			language = self.name_by_shortid[string]
		elif len(string) == 3 and string in self.name_and_shortid_by_longid:
			language = self.name_and_shortid_by_longid[string][1]
		elif len(string) >= 3:
			string = string.capitalize()
			for key in list(self.idlist_by_name.keys()):
				if key == string or _(key) == string:
					language = key
		return language
