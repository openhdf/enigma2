
from Tools.LoadPixmap import LoadPixmap 
from Components.Pixmap import Pixmap 
from Renderer import Renderer 
from enigma import ePixmap, eTimer 
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename 
from Components.config import config

class Picon_Sat(Renderer):
	__module__ = __name__
	searchPaths = ('/usr/share/enigma2/hd-line_tvpro/%s/',
                   '/media/cf/%s/',
                   '/media/hdd/%s/', 
                   '/media/sda1/%s/', 
                   '/media/usb/%s/')
                   
	def __init__(self):
		Renderer.__init__(self)
		self.path = 'piconSat'
		self.nameCache = {}
		self.pngname = ''
		self.pixmaps = []
		self.pixdelay = 100
		self.pics = []
		self.picon_default = "picon_default2.png"
		
	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if (attrib == 'path'):
				self.path = value
			elif (attrib == 'picon_default2'):
				self.picon_default = value
			elif attrib == "pixmaps":
				self.pixmaps = value.split(',')
			elif attrib == "pixdelay":
				self.pixdelay = int(value)
			else:
				attribs.append((attrib, value))
				
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)
		
	GUI_WIDGET = ePixmap
	
	def changed(self, what):
		if self.instance:
			pngname = ''
			if (what[0] != self.CHANGED_CLEAR):
				sname = ""
				service = self.source.service
				if service:
					feinfo = (service and service.frontendInfo())
					if feinfo:
						frontendData = feinfo.getAll(True)
						if frontendData.get("tuner_type") == "DVB-S":
							try:
								sname = {3590: "10W",
								 3592: "08W",
                                                                 3560: "40W",
								 3550: "50W",
								 3530: "70W",
								 3520: "80W",
								 3449: "110W",
								 3475: "125W",
								 3460: "140W",
								 3450: "150W",
								 3420: "180W",
								 3380: "220W",
								 3355: "245W",
								 3325: "275W",
								 3300: "300W",
								 3285: "315W",
								 3170: "430W",
								 3150: "450W",
								 3070: "530W",
								 3045: "555W",
								 3020: "580W",
								 2990: "610W",
								 2900: "700W",
								 2880: "720W",
								 2875: "727W",
								 2860: "740W",
								 2810: "790W",
								 2780: "820W",
								 2690: "910W",
								 2985: "615W",
								 2830: "770W",
								 2630: "970W",
								 2500: "1100W",
								 2502: "1100W",
								 2410: "1190W",
								 2391: "1210W",
								 2390: "1210W",
								 2412: "1190W",
								 2310: "1290W",
								 2311: "1290W",
								 2120: "1480W",
								 1460: "1460E",
								 1440: "1440E",
								 1400: "1400E",
								 1380: "1380E",
								 1220: "1220E",
								 1131: "1131E",
                                                                 1101: "1100E",
								 1100: "1100E",
								 1006: "1005E",
								 1030: "1030E",
								 1056: "1055E",
								 1082: "1082E",
								 881: "880E",
								 965: "965E",
								 900: "900E",
								 917: "915E",
								 950: "950E",
								 951: "950E",
								 765: "765E",
								 785: "785E",
								 800: "800E",
								 830: "830E",
								 852: "852E",
								 750: "750E",
								 720: "720E",
								 705: "705E",
								 685: "685E",
								 620: "620E",
								 600: "600E",
								 570: "570E",
								 560: "560E",
								 530: "530E",
								 480: "480E",
								 450: "450E",
								 420: "420E",
								 400: "400E",
								 390: "390E",
								 380: "380E",
								 361: "361E",
								 360: "360E",
								 335: "335E",
								 330: "330E",
								 328: "328E",
								 315: "315E",
								 310: "310E",
								 305: "305E",
								 285: "285E",
								 284: "282E",
								 282: "282E",
								 260: "260E",
								 255: "255E",
								 235: "235E",
								 215: "215E",
								 216: "216E",
								 210: "210E",
								 192: "192E",
								 160: "160E",
								 130: "130E",
								 100: "100E",
								 90: "90E",
								 70: "70E",
								 50: "50E",
								 48: "48E",
								 30: "30E",
								 20: "20E"}[frontendData.get("orbital_position", "None")]
							except Exception, e:
								pass
				
				pos = sname.rfind(':')
				if (pos != -1):
					sname = sname[:pos].rstrip(':').replace(':', '_')
				pngname = self.nameCache.get(sname, '')
				if (pngname == ''):
					pngname = self.findPicon(sname)
					if (pngname != ''):
						self.nameCache[sname] = pngname
			if (pngname == ''):
				pngname = self.nameCache.get('default', '')
				if (pngname == ''):
					tmp = resolveFilename(SCOPE_CURRENT_SKIN, self.picon_default)
					if fileExists(tmp):
						pngname = tmp
					else:
						pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default2.png')
					self.nameCache['default'] = pngname
					
			if (self.pngname != pngname):
				self.pngname = pngname
				
				self.runAnim()
				
				self.instance.setPixmapFromFile(self.pngname)
					
	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngname = (((path % self.path) + serviceName) + '.png')
			if fileExists(pngname):
				return pngname
				
		return ''
		
	def runAnim(self):
		if len(self.pics) == 0:
			for x in self.pixmaps:
				self.pics.append(LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, x)))
			
		self.slide = len(self.pics)
		self.timer = eTimer()
		self.timer.callback.append(self.timerEvent)
		self.timer.start(self.pixdelay, True)
		
	def timerEvent(self):
		if self.slide > 0:
			self.timer.stop()
			self.instance.setPixmap(self.pics[len(self.pics) - self.slide])
			self.slide = self.slide - 1
			self.timer.start(self.pixdelay, True)
		else:
			self.timer.stop()
			self.instance.setPixmapFromFile(self.pngname)

