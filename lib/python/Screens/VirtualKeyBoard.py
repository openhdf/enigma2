# -*- coding: UTF-8 -*-
from enigma import RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, getPrevAsciiCode, gFont

from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from skin import fonts, parameters
from Tools.Directories import SCOPE_GUISKIN, resolveFilename
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput


class VirtualKeyBoardList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		font = fonts.get("VirtualKeyboard", ("Regular", 28, 45))
		self.l.setFont(0, gFont(font[0], font[1]))
		self.l.setItemHeight(font[2])


class VirtualKeyBoardEntryComponent:
	def __init__(self):
		pass


class VirtualKeyBoard(Screen):
	def __init__(self, session, title=_("Virtual KeyBoard Text:"), currPos=None, **kwargs):
		Screen.__init__(self, session)
		self.setTitle(_("Virtual KeyBoard"))
		self.keys_list = []
		self.shiftkeys_list = []
		self.lang = language.getLanguage()
		self.nextLang = None
		self.shiftMode = False
		self.selectedKey = 0
		self.smsChar = None
		self.sms = NumericalTextInput(self.smsOK)

		self.key_bg = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_bg.png"))
		self.key_sel = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_sel.png"))
		self.key_backspace = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_backspace.png"))
		self.key_all = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_all.png"))
		self.key_clr = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_clr.png"))
		self.key_esc = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_esc.png"))
		self.key_ok = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_ok.png"))
		self.key_shift = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_shift.png"))
		self.key_shift_sel = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_shift_sel.png"))
		self.key_space = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_space.png"))
		self.key_left = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_left.png"))
		self.key_right = LoadPixmap(path=resolveFilename(SCOPE_GUISKIN, "buttons/vkey_right.png"))

		self.keyImages = {"BACKSPACE": self.key_backspace, "CLEAR": self.key_clr, "ALL": self.key_all, "EXIT": self.key_esc, "OK": self.key_ok, "SHIFT": self.key_shift, "SPACE": self.key_space, "LEFT": self.key_left, "RIGHT": self.key_right}
		self.keyImagesShift = {"BACKSPACE": self.key_backspace, "CLEAR": self.key_clr, "EXIT": self.key_esc, "OK": self.key_ok, "SHIFT": self.key_shift_sel, "SPACE": self.key_space, "LEFT": self.key_left, "RIGHT": self.key_right}

		self["country"] = StaticText("")
		self["header"] = Label(title)
		self["text"] = Input(currPos=len(kwargs.get("text", "")), allMarked=False, **kwargs)
		self["list"] = VirtualKeyBoardList([])

		self["actions"] = NumberActionMap(["OkCancelActions", "WizardActions", "ColorActions", "KeyboardInputActions", "InputBoxActions", "InputAsciiActions"],
			{
				"gotAsciiCode": self.keyGotAscii,
				"ok": self.okClicked,
				"OKLong": self.okLongClicked,
				"cancel": self.exit,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
				"red": self.exit,
				"green": self.ok,
				"yellow": self.switchLang,
				"blue": self.shiftClicked,
				"deleteBackward": self.backClicked,
				"deleteForward": self.forwardClicked,
				"back": self.exit,
				"pageUp": self.cursorRight,
				"pageDown": self.cursorLeft,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal,
				"0": self.keyNumberGlobal,
			}, -2)
		self.setLang()
		self.onExecBegin.append(self.setKeyboardModeAscii)
		self.onLayoutFinish.append(self.buildVirtualKeyBoard)
		self.onClose.append(self.__onClose)

	def __onClose(self):
		self.sms.timer.stop()

	def switchLang(self):
		self.lang = self.nextLang
		self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
		if self.lang == "de_DE":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"], ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "@", "ß", "[", "]", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü", "*"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"], [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "|", "^", "OK", "LEFT", "RIGHT"]]
			self.nextLang = "hu_HU"
		elif self.lang == "hu_HU":
			self.keys_list = [["EXIT", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ő", "ú"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "é", "á", "ű"], ["í", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "ö", "ü", "ó", "#", "@", "*", "OK", "LEFT", "RIGHT", "CLEAR"]]
			self.shiftkeys_list = [["EXIT", "§", "'", '"', "+", "!", "%", "/", "=", "(", ")", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ő", "Ú"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "É", "Á", "Ű"], ["Í", "Y", "X", "C", "V", "B", "N", "M", "?", ":", "_", ";"], ["SHIFT", "Ö", "Ü", "Ó", "&", "<", ">", "{", "}", "[", "]", "\\"]]
			self.nextLang = "es_ES"
		elif self.lang == "es_ES":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "¡", "'"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ñ", "ç", "+"], ["<", "z", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "@", "á", "é", "í", "ó", "ú", "ü", "º", "ª", "OK"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "·", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "¿", "?"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ñ", "Ç", "*"], [">", "Z", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "€", "Á", "É", "Í", "Ó", "Ú", "Ü", "[", "]", "OK"]]
			self.nextLang = "fi_FI"
		elif self.lang == "fi_FI":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "é", "+"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"], ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "@", "ß", "ĺ", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "É", "*"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"], [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "Ĺ", "OK", "LEFT", "RIGHT"]]
			self.nextLang = "lv_LV"
		elif self.lang == "lv_LV":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "-", "š"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "ū"], ["<", "z", "x", "c", "v", "b", "n", "m", ",", ".", "ž", "ALL"], ["SHIFT", "SPACE", "ā", "č", "ē", "ģ", "ī", "ķ", "ļ", "ņ", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", "@", "$", "*", "(", ")", "_", "=", "/", "\\", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "+", "Š"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", ":", '"', "Ū"], [">", "Z", "X", "C", "V", "B", "N", "M", "#", "?", "Ž", "CLEAR"], ["SHIFT", "SPACE", "Ā", "Č", "Ē", "Ģ", "Ī", "Ķ", "Ļ", "Ņ", "LEFT", "RIGHT"]]
			self.nextLang = "ru_RU"
		elif self.lang == "ru_RU":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "+"], ["к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "#"], ["<", "х", "ц", "ч", "ш", "щ", "ъ", "ы", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "@", "ь", "э", "ю", "я", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "*"], ["К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "'"], [">", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ", "Ы", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "Ь", "Э", "Ю", "Я", "OK", "LEFT", "RIGHT"]]
			self.nextLang = "sv_SE"
		elif self.lang == "sv_SE":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "é", "+"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"], ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "@", "ß", "ĺ", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "É", "*"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"], [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "Ĺ", "OK", "LEFT", "RIGHT"]]
			self.nextLang = "sk_SK"
		elif self.lang == "sk_SK":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ú", "+"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ľ", "@", "#"], ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "š", "č", "ž", "ý", "á", "í", "é", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "ť", "*"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "ň", "ď", "'"], ["Á", "É", "Ď", "Í", "Ý", "Ó", "Ú", "Ž", "Š", "Č", "Ť", "Ň"], [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "ä", "ö", "ü", "ô", "ŕ", "ĺ", "OK"]]
			self.nextLang = "cs_CZ"
		elif self.lang == "cs_CZ":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ú", "+"], ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ů", "@", "#"], ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "ALL"], ["SHIFT", "SPACE", "ě", "š", "č", "ř", "ž", "ý", "á", "í", "é", "OK"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "ť", "*"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "ň", "ď", "'"], [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "Č", "Ř", "Š", "Ž", "Ú", "Á", "É", "OK"]]
			self.nextLang = "el_GR"
		elif self.lang == "el_GR":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["=", "ς", "ε", "ρ", "τ", "υ", "θ", "ι", "ο", "π", "[", "]"], ["α", "σ", "δ", "φ", "γ", "η", "ξ", "κ", "λ", ";", "'", "-"], ["\\", "ζ", "χ", "ψ", "ω", "β", "ν", "μ", ",", ".", "/", "ALL"], ["SHIFT", "SPACE", "ά", "έ", "ή", "ί", "ό", "ύ", "ώ", "ϊ", "ϋ", "OK"]]
			self.shiftkeys_list = [["EXIT", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "BACKSPACE"], ["+", "€", "Ε", "Ρ", "Τ", "Υ", "Θ", "Ι", "Ο", "Π", "{", "}"], ["Α", "Σ", "Δ", "Φ", "Γ", "Η", "Ξ", "Κ", "Λ", ":", '"', "_"], ["|", "Ζ", "Χ", "Ψ", "Ω", "Β", "Ν", "Μ", "<", ">", "?", "CLEAR"], ["SHIFT", "SPACE", "Ά", "Έ", "Ή", "Ί", "Ό", "Ύ", "Ώ", "Ϊ", "Ϋ", "OK"]]
			self.nextLang = "pl_PL"
		elif self.lang == "pl_PL":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "-", "["], ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "\\"], ["<", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "ALL"], ["SHIFT", "SPACE", "ą", "ć", "ę", "ł", "ń", "ó", "ś", "ź", "ż", "OK"]]
			self.shiftkeys_list = [["EXIT", "!", "@", "#", "$", "%", "^", "&", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "*", "]"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "?", '"', "|"], [">", "Z", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "Ą", "Ć", "Ę", "Ł", "Ń", "Ó", "Ś", "Ź", "Ż", "OK"]]
			self.nextLang = "ar_AE"
		elif self.lang == "ar_AE":
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["ض", "ص", "ث", "ق", "ف", "غ", "ع", "ه", "خ", "ح", "ج", "د"], ["ش", "س", "ي", "ب", "ل", "ا", "ت", "ن", "م", "ك", "ط", "#"], ["ئ", "ء", "ؤ", "ر", "لا", "ى", "ة", "و", "ز", "ظ", "ذ", "ALL"], ["SHIFT", "SPACE", "+", "-", "*", "/", ".", ",", "@", "%", "&", "OK"]]
			self.shiftkeys_list = [["EXIT", "!", '"', "§", "$", "^", "<", ">", "(", ")", "=", "BACKSPACE"], ["َ", "ً", "ُ", "ٌ", "لإ", "إ", "‘", "÷", "×", "؛", "<", ">"], ["ِ", "ٍ", "]", "[", "لأ", "أ", "ـ", "،", "/", ":", "~", "'"], ["ْ", "}", "{", "لآ", "آ", "’", ",", ".", "؟", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "?", "\\", "=", "ّ", "~", "OK"]]
			self.nextLang = "th_TH"
		elif self.lang == "th_TH":
			self.keys_list = [["EXIT", "\xe0\xb9\x85", "\xe0\xb8\xa0", "\xe0\xb8\x96", "\xe0\xb8\xb8", "\xe0\xb8\xb6", "\xe0\xb8\x84", "\xe0\xb8\x95", "\xe0\xb8\x88", "\xe0\xb8\x82", "\xe0\xb8\x8a", "BACKSPACE"], ["\xe0\xb9\x86", "\xe0\xb9\x84", "\xe0\xb8\xb3", "\xe0\xb8\x9e", "\xe0\xb8\xb0", "\xe0\xb8\xb1", "\xe0\xb8\xb5", "\xe0\xb8\xa3", "\xe0\xb8\x99", "\xe0\xb8\xa2", "\xe0\xb8\x9a", "\xe0\xb8\xa5"], ["\xe0\xb8\x9f", "\xe0\xb8\xab", "\xe0\xb8\x81", "\xe0\xb8\x94", "\xe0\xb9\x80", "\xe0\xb9\x89", "\xe0\xb9\x88", "\xe0\xb8\xb2", "\xe0\xb8\xaa", "\xe0\xb8\xa7", "\xe0\xb8\x87", "\xe0\xb8\x83"], ["\xe0\xb8\x9c", "\xe0\xb8\x9b", "\xe0\xb9\x81", "\xe0\xb8\xad", "\xe0\xb8\xb4", "\xe0\xb8\xb7", "\xe0\xb8\x97", "\xe0\xb8\xa1", "\xe0\xb9\x83", "\xe0\xb8\x9d", "", "ALL"], ["SHIFT", "SPACE", "OK", "LEFT", "RIGHT"]]
			self.shiftkeys_list = [["EXIT", "\xe0\xb9\x91", "\xe0\xb9\x92", "\xe0\xb9\x93", "\xe0\xb9\x94", "\xe0\xb8\xb9", "\xe0\xb9\x95", "\xe0\xb9\x96", "\xe0\xb9\x97", "\xe0\xb9\x98", "\xe0\xb9\x99", "BACKSPACE"], ["\xe0\xb9\x90", "", "\xe0\xb8\x8e", "\xe0\xb8\x91", "\xe0\xb8\x98", "\xe0\xb9\x8d", "\xe0\xb9\x8a", "\xe0\xb8\x93", "\xe0\xb8\xaf", "\xe0\xb8\x8d", "\xe0\xb8\x90", "\xe0\xb8\x85"], ["\xe0\xb8\xa4", "\xe0\xb8\x86", "\xe0\xb8\x8f", "\xe0\xb9\x82", "\xe0\xb8\x8c", "\xe0\xb9\x87", "\xe0\xb9\x8b", "\xe0\xb8\xa9", "\xe0\xb8\xa8", "\xe0\xb8\x8b", "", "\xe0\xb8\xbf"], ["", "", "\xe0\xb8\x89", "\xe0\xb8\xae", "\xe0\xb8\xba", "\xe0\xb9\x8c", "", "\xe0\xb8\x92", "\xe0\xb8\xac", "\xe0\xb8\xa6", "", "CLEAR"], ["SHIFT", "SPACE", "OK", "LEFT", "RIGHT"]]
			self.nextLang = "en_US"
		else:
			self.keys_list = [["EXIT", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "BACKSPACE"], ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "-", "["], ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "\\"], ["<", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "ALL"], ["SHIFT", "SPACE", "OK", "LEFT", "RIGHT", "*"]]
			self.shiftkeys_list = [["EXIT", "!", "@", "#", "$", "%", "^", "&", "(", ")", "=", "BACKSPACE"], ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "+", "]"], ["A", "S", "D", "F", "G", "H", "J", "K", "L", "?", '"', "|"], [">", "Z", "X", "C", "V", "B", "N", "M", ";", ":", "_", "CLEAR"], ["SHIFT", "SPACE", "|", "^", "OK", "LEFT", "RIGHT", "~"]]
			self.lang = "en_US"
			self.nextLang = "de_DE"
		self["country"].setText(self.lang)

	def virtualKeyBoardEntryComponent(self, keys):
		w, h = parameters.get("VirtualKeyboard", (45, 45))
		key_bg_width = self.key_bg and self.key_bg.size().width() or w
		key_images = self.shiftMode and self.keyImagesShift or self.keyImages
		res = [keys]
		text = []
		x = 0
		for key in keys:
			png = key_images.get(key, None)
			if png:
				width = png.size().width()
				res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=png))
			else:
				width = key_bg_width
				res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_bg))
				text.append(MultiContentEntryText(pos=(x, 0), size=(width, h), font=0, text=key, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER))
			x += width
		return res + text

	def buildVirtualKeyBoard(self):
		self.previousSelectedKey = None
		self.list = []
		self.max_key = 0
		for keys in self.shiftMode and self.shiftkeys_list or self.keys_list:
			self.list.append(self.virtualKeyBoardEntryComponent(keys))
			self.max_key += len(keys)
		self.max_key -= 1
		self.markSelectedKey()

	def markSelectedKey(self):
		w, h = parameters.get("VirtualKeyboard", (45, 45))
		if self.previousSelectedKey is not None:
			self.list[self.previousSelectedKey // 12] = self.list[self.previousSelectedKey // 12][:-1]
		width = self.key_sel.size().width()
		try:
			x = self.list[self.selectedKey // 12][self.selectedKey % 12 + 1][1]
		except IndexError:
			self.selectedKey = self.max_key
			x = self.list[self.selectedKey // 12][self.selectedKey % 12 + 1][1]
		self.list[self.selectedKey // 12].append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_sel))
		self.previousSelectedKey = self.selectedKey
		self["list"].setList(self.list)

	def backClicked(self):
		self["text"].deleteBackward()

	def forwardClicked(self):
		self["text"].deleteForward()

	def shiftClicked(self):
		self.smsChar = None
		self.shiftMode = not self.shiftMode
		self.buildVirtualKeyBoard()

	def okClicked(self):
		self.smsChar = None
		text = (self.shiftMode and self.shiftkeys_list or self.keys_list)[self.selectedKey // 12][self.selectedKey % 12]

		if text == "EXIT":
			self.close(None)

		elif text == "BACKSPACE":
			self["text"].deleteBackward()

		elif text == "ALL":
			self["text"].markAll()

		elif text == "CLEAR":
			self["text"].deleteAllChars()
			self["text"].update()

		elif text == "SHIFT":
			self.shiftClicked()

		elif text == "SPACE":
			self["text"].char((" "))

		elif text == "OK":
			self.close(self["text"].getText())

		elif text == "LEFT":
			self["text"].left()

		elif text == "RIGHT":
			self["text"].right()

		else:
			self["text"].char(text)

	def okLongClicked(self):
		self.smsChar = None
		text = (self.shiftMode and self.shiftkeys_list or self.keys_list)[self.selectedKey // 12][self.selectedKey % 12]

		if text == "BACKSPACE":
			self["text"].deleteAllChars()
			self["text"].update()

	def ok(self):
		self.close(self["text"].getText())

	def exit(self):
		self.close(None)

	def cursorRight(self):
		self["text"].right()

	def cursorLeft(self):
		self["text"].left()

	def left(self):
		self.smsChar = None
		self.selectedKey = self.selectedKey // 12 * 12 + (self.selectedKey + 11) % 12
		if self.selectedKey > self.max_key:
			self.selectedKey = self.max_key
		self.markSelectedKey()

	def right(self):
		self.smsChar = None
		self.selectedKey = self.selectedKey // 12 * 12 + (self.selectedKey + 1) % 12
		if self.selectedKey > self.max_key:
			self.selectedKey = self.selectedKey // 12 * 12
		self.markSelectedKey()

	def up(self):
		self.smsChar = None
		self.selectedKey -= 12
		if self.selectedKey < 0:
			self.selectedKey = self.max_key // 12 * 12 + self.selectedKey % 12
			if self.selectedKey > self.max_key:
				self.selectedKey -= 12
		self.markSelectedKey()

	def down(self):
		self.smsChar = None
		self.selectedKey += 12
		if self.selectedKey > self.max_key:
			self.selectedKey %= 12
		self.markSelectedKey()

	def keyNumberGlobal(self, number):
		self.smsChar = self.sms.getKey(number)
		self.selectAsciiKey(self.smsChar)

	def smsOK(self):
		if self.smsChar and self.selectAsciiKey(self.smsChar):
			print("pressing ok now")
			self.okClicked()

	def keyGotAscii(self):
		self.smsChar = None
		if self.selectAsciiKey(str(chr(getPrevAsciiCode()))):
			self.okClicked()

	def selectAsciiKey(self, char):
		if char == " ":
			char = "SPACE"
		for keyslist in (self.shiftkeys_list, self.keys_list):
			selkey = 0
			for keys in keyslist:
				for key in keys:
					if key == char:
						self.selectedKey = selkey
						if self.shiftMode != (keyslist is self.shiftkeys_list):
							self.shiftMode = not self.shiftMode
							self.buildVirtualKeyBoard()
						else:
							self.markSelectedKey()
						return True
					selkey += 1
		return False
