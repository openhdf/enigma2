from __future__ import division

# ============================================================
# SUPPORT / ERROR CONTEXT LOGGER FOR SKIN, XML, CONVERTER,
# RENDERER AND PLUGIN RELATED PYTHON EXCEPTIONS
#
# PURPOSE
#   Show real errors with enough context to identify the failing place.
#   Intended for support, debugging and fixing skin/plugin issues.
#
# WHAT IT COVERS
#   - XML parse errors
#   - readSkin / applySkin / applyAllAttributes related errors
#   - invalid or unsupported widget attributes
#   - color / font / pixmap / scrollbar / padding / itemHeight issues
#   - converter import / instantiate / connect errors
#   - renderer import / instantiate / connect errors
#   - unhandled Python exceptions from plugins
#
# CONTEXT INCLUDED WHEN AVAILABLE
#   - screen class / selected skin screen / requested names
#   - widget name / source / render
#   - converter type / converter arguments
#   - GUI object type
#   - attribute name / raw attribute value
#   - XML file / probable line locator / XML snippet
#   - exception type / exception text
#   - traceback details when verbose is enabled
#
# SETTINGS
#   SKIN_ERROR_CONTEXT   = True   -> enable support logger
#   SKIN_ERROR_CONTEXT   = False  -> disable support logger
#   SKIN_HELPER_VERBOSE  = True   -> include traceback details
#   SKIN_HELPER_VERBOSE  = False  -> compact error output
#   SKIN_DEEP_PLUGIN_DEBUG = True -> reserved support switch, no ActionMap hook
#   SKIN_DEEP_PLUGIN_DEBUG = False-> reserved support switch, no ActionMap hook
#
# IMPORTANT
#   This switch is intentionally decoupled from ActionMap/standby runtime hooks.
#   Changing it will not install key/action hooks and should not affect standby.
#   It remains at the top for compatibility and future support variants.
#
# RECOMMENDED
#   Daily support:
#       SKIN_ERROR_CONTEXT = True
#       SKIN_HELPER_VERBOSE = True
#       SKIN_DEEP_PLUGIN_DEBUG = False
#
#   Safe maximum support:
#       SKIN_ERROR_CONTEXT = True
#       SKIN_HELPER_VERBOSE = True
#       SKIN_DEEP_PLUGIN_DEBUG = True
#   Note: in this safe build, True/False does not enable ActionMap hooking.
# ============================================================

from errno import ENOENT
from os import listdir
from os.path import basename, dirname, isfile
from os.path import join as pathjoin
from xml.etree.ElementTree import (Element, ElementTree, ParseError,
                                    fromstring, parse)

from enigma import (BT_ALPHABLEND, BT_ALPHATEST, addFont, eLabel, ePixmap,
                    ePoint, eRect, eSize, eWindow, eWindowStyleManager,
                    eWindowStyleSkinned, getDesktop, getFontFaces, gFont, gRGB)
from six import ensure_str

from Components.config import ConfigSubsection, ConfigText, config
from Components.RcModel import rc_model
from Components.Sources.Source import ObsoleteSource
from Components.SystemInfo import BoxInfo
from Tools.Directories import (SCOPE_CURRENT_LCDSKIN, SCOPE_CURRENT_SKIN,
                               SCOPE_FONTS, SCOPE_GUISKIN, SCOPE_SKIN,
                               pathExists, resolveFilename)
from Tools.Import import my_import
from Tools.LoadPixmap import LoadPixmap

if config.usage.skin_error_context.value:
	SKIN_ERROR_CONTEXT = True
else:
	SKIN_ERROR_CONTEXT = False
if config.usage.skin_helper_verbose.value:
	SKIN_HELPER_VERBOSE = True
else:
	SKIN_HELPER_VERBOSE = False
if config.usage.skin_error_plugin_debug.value:
	SKIN_DEEP_PLUGIN_DEBUG = True
else:
	SKIN_DEEP_PLUGIN_DEBUG = False

#SKIN_HELPER_VERBOSE = True
#SKIN_ERROR_CONTEXT = True
#SKIN_DEEP_PLUGIN_DEBUG = True

DEFAULT_SKIN = "XionHDF/skin.xml"
EMERGENCY_SKIN = "skin_default/skin.xml"
EMERGENCY_NAME = "Stone II"
DEFAULT_DISPLAY_SKIN = "lcd_skin/skin_display_picon_01.xml"
DEFAULT_STANDBY_SKIN = "lcd_skin/skin_standby_default.xml"
USER_SKIN = "skin_user.xml"
USER_SKIN_TEMPLATE = "skin_user_%s.xml"
SUBTITLE_SKIN = "skin_subtitles.xml"

GUI_SKIN_ID = 0  # Main frame-buffer.
DISPLAY_SKIN_ID = 1  # Front panel / display / LCD.

domScreens = {}  # Dictionary of skin based screens.
colors = {  # Dictionary of skin color names.
	"key_back": gRGB(0x00313131),
	"key_blue": gRGB(0x0018188b),
	"key_green": gRGB(0x001f771f),
	"key_red": gRGB(0x009f1313),
	"key_text": gRGB(0x00ffffff),
	"key_yellow": gRGB(0x00a08500)
}
BodyFont = ("Regular", 20, 24, 18) # font which is used when a font alias definition is missing from the "fonts" dict.
fonts = {  # Dictionary of predefined and skin defined font aliases.
	"Body": BodyFont
}
menus = {}  # Dictionary of images associated with menu entries.
parameters = {}  # Dictionary of skin parameters used to modify code behavior.
setups = {}  # Dictionary of images associated with setup menus.
switchPixmap = {}  # Dictionary of switch images.
windowStyles = {}  # Dictionary of window styles for each screen ID.
globalScrollbarDefaults = {"width": "16", "borderWidth": "2", "borderColorName": "scrollbarBorderColor", "sliderColorName": "scrollbarSliderColor"}  # Global scrollbar defaults.
constantWidgets = {}
variables = {}

config.skin = ConfigSubsection()
skin = resolveFilename(SCOPE_SKIN, DEFAULT_SKIN)
if not isfile(skin):
	print("[Skin] Error: Default skin '%s' is not readable or is not a file!  Using emergency skin." % skin)
	DEFAULT_SKIN = EMERGENCY_SKIN
config.skin.primary_skin = ConfigText(default=DEFAULT_SKIN)
config.skin.display_skin = ConfigText(default=DEFAULT_DISPLAY_SKIN)
config.skin.standby_skin = ConfigText(default=DEFAULT_STANDBY_SKIN)

currentPrimarySkin = None
currentDisplaySkin = None
currentStandbySkin = None
callbacks = []
runCallbacks = False

# Skins are loaded in order of priority.  Skin with highest priority is
# loaded last.  This is usually the user-specified skin.  In this way
# any duplicated screens will be replaced by a screen of the same name
# with a higher priority.
#
# GUI skins are saved in the settings file as the path relative to
# SCOPE_SKIN.  The full path is NOT saved.  E.g. "MySkin/skin.xml"
#
# Display skins are saved in the settings file as the path relative to
# SCOPE_CURRENT_LCDSKIN.  The full path is NOT saved.
# E.g. "MySkin/skin_display.xml"
#


def InitSkins():
	global currentPrimarySkin, currentDisplaySkin, currentStandbySkin
	runCallbacks = False
	# Add the emergency skin.  This skin should provide enough functionality
	# to enable basic GUI functions to work.
	loadSkin(EMERGENCY_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	# Add the subtitle skin.
	loadSkin(SUBTITLE_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	if BoxInfo.getItem("OledDisplay"):
		# Add the front panel / display / lcd skin.
		result = []
		for skin, name in [(config.skin.display_skin.value, "current"), (DEFAULT_DISPLAY_SKIN, "default")]:
			if skin in result:  # Don't try to add a skin that has already failed.
				continue
			config.skin.display_skin.value = skin
			if loadSkin(config.skin.display_skin.value, scope=SCOPE_CURRENT_LCDSKIN, desktop=getDesktop(DISPLAY_SKIN_ID), screenID=DISPLAY_SKIN_ID):
				currentDisplaySkin = config.skin.display_skin.value
				break
			print("[Skin] Error: Adding %s display skin '%s' has failed!" % (name, config.skin.display_skin.value))
			result.append(skin)
		result = []
		for skin, name in [(config.skin.standby_skin.value, "current"), (DEFAULT_STANDBY_SKIN, "default")]:
			if skin in result:  # Don't try to add a skin that has already failed.
				continue
			config.skin.standby_skin.value = skin
			if loadSkin(config.skin.standby_skin.value, scope=SCOPE_CURRENT_LCDSKIN, desktop=getDesktop(DISPLAY_SKIN_ID), screenID=DISPLAY_SKIN_ID):
				currentStandbySkin = config.skin.standby_skin.value
				break
			print("[Skin] Error: Adding %s display skin '%s' has failed!" % (name, config.skin.standby_skin.value))
			result.append(skin)
	# Add the main GUI skin.
	result = []
	for skin, name in [(config.skin.primary_skin.value, "current"), (DEFAULT_SKIN, "default")]:
		if skin in result:  # Don't try to add a skin that has already failed.
			continue
		config.skin.primary_skin.value = skin
		if loadSkin(config.skin.primary_skin.value, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID):
			currentPrimarySkin = config.skin.primary_skin.value
			break
		print("[Skin] Error: Adding %s GUI skin '%s' has failed!" % (name, config.skin.primary_skin.value))
		result.append(skin)
	if currentPrimarySkin != None:
		partsDir = resolveFilename(SCOPE_GUISKIN, pathjoin(dirname(currentPrimarySkin), "mySkin", ""))
		if pathExists(partsDir) and currentPrimarySkin != DEFAULT_SKIN:
			for file in sorted(listdir(partsDir)):
				if file.startswith("skin_") and file.endswith(".xml"):
					partsFile = pathjoin(partsDir, file)
					if not loadSkin(partsFile, scope=SCOPE_GUISKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID):
						print("[Skin] Error: Failed to load additionally skin file '%s'!" % partsFile)
	# Add an optional skin related user skin "user_skin_<SkinName>.xml".  If there is
	# not a skin related user skin then try to add am optional generic user skin.
	result = None
	if isfile(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)):
		name = USER_SKIN_TEMPLATE % dirname(config.skin.primary_skin.value)
		if isfile(resolveFilename(SCOPE_CURRENT_SKIN, name)):
			result = loadSkin(name, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	if result is None:
		loadSkin(USER_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	runCallbacks = True

# Temporary entry point for older versions of StartEnigma.py.
#


def restoreSkin():
	try:
		skinrestorefile = "/media/hdd/images/skinrestore"
		from Tools.Directories import fileExists
		if fileExists(skinrestorefile):
			from os import remove
			remove(skinrestorefile)
			print("[SkinRestore]: Skinrestorefile found and removed")
			if config.skin.primary_skin.value == "XionHDF/skin.xml":
				from Plugins.Extensions.XionHDF.save import justSave
				print("[SkinRestore]: Starting restore XionHDF")
				justSave()
			elif config.skin.primary_skin.value == "KravenHD/skin.xml":
				from Plugins.Extensions.KravenHD.save import justSave
				print("[SkinRestore]: Starting restore KravenHD")
				justSave()
			elif config.skin.primary_skin.value == "PlatoonHD/skin.xml":
				from Plugins.Extensions.PlatoonHD.save import justSave
				print("[SkinRestore]: Start restoring PlatoonHD")
				justSave()
	except:
		print("[SkinRestore]: restore failed")


def loadSkinData(desktop):
	restoreSkin()
	InitSkins()

# Method to load a skin XML file into the skin data structures.
#


def loadSkin(filename, scope=SCOPE_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID):
	global windowStyles
	filename = resolveFilename(scope, filename)
	print("[Skin] Loading skin file '%s'." % filename)
	try:
		with open(filename, "r") as fd:  # This open gets around a possible file handle leak in Python's XML parser.
			try:
				domSkin = parse(fd).getroot()
				# print("[Skin] DEBUG: Extracting non screen blocks from '%s'.  (scope='%s')" % (filename, scope))
				# For loadSingleSkinData colors, bordersets etc. are applied one after
				# the other in order of ascending priority.
				loadSingleSkinData(desktop, screenID, domSkin, filename, scope=scope)
				for element in domSkin:
					if element.tag == "screen":  # Process all screen elements.
						name = element.attrib.get("name", None)
						if name:  # Without a name, it's useless!
							scrnID = element.attrib.get("id", None)
							if scrnID is None or scrnID == screenID:  # If there is a screen ID is it for this display.
								# print("[Skin] DEBUG: Extracting screen '%s' from '%s'.  (scope='%s')" % (name, filename, scope))
								domScreens[name] = (element, "%s/" % dirname(filename))
					elif element.tag == "windowstyle":  # Process the windowstyle element.
						scrnID = element.attrib.get("id", None)
						if scrnID is not None:  # Without an scrnID, it is useless!
							scrnID = int(scrnID)
							# print("[Skin] DEBUG: Processing a windowstyle ID='%s'." % scrnID)
							domStyle = ElementTree(Element("skin"))
							domStyle.getroot().append(element)
							windowStyles[scrnID] = (desktop, screenID, domStyle.getroot(), filename, scope)
					# Element is not a screen or windowstyle element so no need for it any longer.
				reloadWindowStyles()  # Reload the window style to ensure all skin changes are taken into account.
				print("[Skin] Loading skin file '%s' complete." % filename)
				if runCallbacks:
					for method in self.callbacks:
						if method:
							method()
				return True
			except ParseError as err:
				fd.seek(0)
				content = fd.readlines()
				line, column = err.position
				print("[Skin] XML Parse Error: '%s' in '%s'!" % (err, filename))
				data = content[line - 1].replace("\t", " ").rstrip()
				print("[Skin] XML Parse Error: '%s'" % data)
				print("[Skin] XML Parse Error: '%s^%s'" % ("-" * column, " " * (len(data) - column - 1)))
			except Exception as err:
				print("[Skin] Error: Unable to parse skin data in '%s' - '%s'!" % (filename, err))
	except (IOError, OSError) as err:
		if err.errno == ENOENT:  # No such file or directory
			print("[Skin] Warning: Skin file '%s' does not exist!" % filename)
		else:
			print("[Skin] Error %d: Opening skin file '%s'! (%s)" % (err.errno, filename, err.strerror))
	except Exception as err:
		print("[Skin] Error: Unexpected error opening skin file '%s'! (%s)" % (filename, err))
	return False


def reloadSkins():
	domScreens.clear()
	colors.clear()
	colors = {
		"key_back": gRGB(0x00313131),
		"key_blue": gRGB(0x0018188b),
		"key_green": gRGB(0x001f771f),
		"key_red": gRGB(0x009f1313),
		"key_text": gRGB(0x00ffffff),
		"key_yellow": gRGB(0x00a08500)
	}
	fonts.clear()
	fonts = {
		"Body": BodyFont
	}
	menus.clear()
	parameters.clear()
	setups.clear()
	switchPixmap.clear()
	InitSkins()


def addCallback(callback):
	if callback not in callbacks:
		callbacks.append(callback)


def removeCallback(callback):
	if callback in self.callbacks:
		callbacks.remove(callback)


class SkinError(Exception):
	def __init__(self, message):
		self.msg = message

	def __str__(self):
		return "[Skin] {%s}: %s!  Please contact the skin's author!" % (config.skin.primary_skin.value, self.msg)

# Convert a coordinate string into a number.  Used to convert object position and
# size attributes into a number.
#    s is the input string.
#    e is the the parent object size to do relative calculations on parent
#    size is the size of the object size (e.g. width or height)
#    font is a font object to calculate relative to font sizes
# Note some constructs for speeding up simple cases that are very common.
#
# Can do things like:  10+center-10w+4%
# To center the widget on the parent widget,
#    but move forward 10 pixels and 4% of parent width
#    and 10 character widths backward
# Multiplication, division and subexpressions are also allowed: 3*(e-c/2)
#
# Usage:  center : Center the object on parent based on parent size and object size.
#         e      : Take the parent size/width.
#         c      : Take the center point of parent size/width.
#         %      : Take given percentage of parent size/width.
#         w      : Multiply by current font width. (Only to be used in elements where the font attribute is available, i.e. not "None")
#         h      : Multiply by current font height. (Only to be used in elements where the font attribute is available, i.e. not "None")
#         f      : Replace with getSkinFactor().
#


def parseCoordinate(s, e, size=0, font=None):
	orig = s = s.strip()
	if s == "center":  # For speed as this can be common case.
		val = 0 if not size else (e - size) // 2
	elif s == "*":
		return None
	else:
		try:
			val = int(s)  # For speed try a simple number first.
		except ValueError:
			if font is None and ("w" in s or "h" in s):
				print("[Skin] Error: 'w' or 'h' is being used in a field where neither is valid. Input string: '%s'" % orig)
				return 0
			if "center" in s:
				s = s.replace("center", str((e - size) / 2.0))
			if "e" in s:
				s = s.replace("e", str(e))
			if "c" in s:
				s = s.replace("c", str(e / 2.0))
			if "w" in s:
				s = s.replace("w", "*%s" % str(fonts[font][3]))
			if "h" in s:
				s = s.replace("h", "*%s" % str(fonts[font][2]))
			if "%" in s:
				s = s.replace("%", "*%s" % str(e / 100.0))
			if "f" in s:
				s = s.replace("f", str(getSkinFactor()))
			try:
				val = int(s)  # For speed try a simple number first.
			except ValueError:
				try:
					val = int(eval(s))
				except Exception as err:
					print("[Skin] %s '%s': Coordinate '%s', processed to '%s', cannot be evaluated!" % (type(err).__name__, err, orig, s))
					val = 0
	# print("[Skin] DEBUG: parseCoordinate s='%s', e='%s', size=%s, font='%s', val='%s'." % (s, e, size, font, val))
	return val


def getParentSize(object, desktop):
	if object:
		parent = object.getParent()
		# For some widgets (e.g. ScrollLabel) the skin attributes are applied to a
		# child widget, instead of to the widget itself.  In that case, the parent
		# we have here is not the real parent, but it is the main widget.  We have
		# to go one level higher to get the actual parent.  We can detect this
		# because the 'parent' will not have a size yet.  (The main widget's size
		# will be calculated internally, as soon as the child widget has parsed the
		# skin attributes.)
		if parent and parent.size().isEmpty():
			parent = parent.getParent()
		if parent:
			return parent.size()
		elif desktop:
			return desktop.size()  # Widget has no parent, use desktop size instead for relative coordinates.
	return eSize()


def parseValuePair(s, scale, object=None, desktop=None, size=None):
	x, y = s.split(",")
	parentsize = eSize()
	if object and ("c" in x or "c" in y or "e" in x or "e" in y or "%" in x or "%" in y):  # Need parent size for ce%
		parentsize = getParentSize(object, desktop)
	xval = parseCoordinate(x, parentsize.width(), size and size.width() or 0)
	yval = parseCoordinate(y, parentsize.height(), size and size.height() or 0)
	return (xval * scale[0][0] // scale[0][1], yval * scale[1][0] // scale[1][1])


def parsePosition(s, scale, object=None, desktop=None, size=None):
	return ePoint(*parseValuePair(s, scale, object, desktop, size))


def parseSize(s, scale, object=None, desktop=None):
	return eSize(*[max(0, x) for x in parseValuePair(s, scale, object, desktop)])


def parseFont(s, scale=((1, 1), (1, 1))):
	if ";" in s:
		name, size = s.split(";")
		orig = size
		try:
			size = int(size)
		except ValueError:
			try:
				size = size.replace("f", str(getSkinFactor()))
				size = int(eval(size))
			except Exception as err:
				print("[Skin] %s '%s': font size formula '%s', processed to '%s', cannot be evaluated!" % (type(err).__name__, err, orig, s))
				size = None
	else:
		name = s
		size = None
	try:
		f = fonts[name]
		name = f[0]
		size = f[1] if size is None else size
	except KeyError:
		if name not in getFontFaces():
			f = fonts["Body"]
			print("[Skin] Error: Font '%s' (in '%s') is not defined!  Using 'Body' font ('%s') instead." % (name, s, f[0]))
			name = f[0]
			size = f[1] if size is None else size
	return gFont(name, int(size) * scale[0][0] // scale[0][1])


def parseColor(s):
	if s[0] != "#":
		try:
			return colors[s]
		except KeyError:
			raise SkinError("Color '%s' must be #aarrggbb or valid named color" % s)
	return gRGB(int(s[1:], 0x10))


def parseParameter(s):
	"""This function is responsible for parsing parameters in the skin, it can parse integers, floats, hex colors, hex integers, named colors, fonts and strings."""
	if s[0] == "*":  # String.
		return s[1:]
	elif s[0] == "#":  # HEX Color.
		return int(s[1:], 16)
	elif s[:2] == "0x":  # HEX Integer.
		return int(s, 16)
	elif "." in s:  # Float number.
		return float(s)
	elif s in colors:  # Named color.
		return colors[s].argb()
	elif s.find(";") != -1:  # Font.
		font, size = [x.strip() for x in s.split(";", 1)]
		return [font, parseScale(size)]
	else:  # Integer.
		return parseScale(s)


def parseScale(s):
	orig = s
	try:
		val = int(s)
	except ValueError:
		try:
			s = s.replace("f", str(getSkinFactor()))
			val = int(eval(s))
		except Exception as err:
			print("[Skin] %s '%s': size formula '%s', processed to '%s', cannot be evaluated!" % (type(err).__name__, err, orig, s))
			val = 0
	return val


def loadPixmap(path, desktop, width=0, height=0):
	option = path.find("#")
	if option != -1:
		path = path[:option]
	if rc_model.rcIsDefault() is False and basename(path) in ("rc.png", "rc0.png", "rc1.png", "rc2.png", "oldrc.png"):
		path = rc_model.getRcImg()
	pixmap = LoadPixmap(path, desktop, None, width, height)
	if pixmap is None:
		raise SkinError("Pixmap file '%s' not found" % path)
	return pixmap


def collectAttributes(skinAttributes, node, context, skinPath=None, ignore=(), filenames=frozenset(("pixmap", "pointer", "seek_pointer", "backgroundPixmap", "selectionPixmap", "sliderPixmap", "scrollbarSliderPicture", "scrollbarbackgroundPixmap", "scrollbarBackgroundPicture"))):
	size = None
	pos = None
	font = None
	for attrib, value in node.items():  # Walk all attributes.
		if attrib not in ignore:
			if attrib in filenames:
				value = resolveFilename(SCOPE_CURRENT_SKIN, value, path_prefix=skinPath)
			# Bit of a hack this, really.  When a window has a flag (e.g. wfNoBorder)
			# it needs to be set at least before the size is set, in order for the
			# window dimensions to be calculated correctly in all situations.
			# If wfNoBorder is applied after the size has been set, the window will
			# fail to clear the title area.  Similar situation for a scrollbar in a
			# listbox; when the scrollbar setting is applied after the size, a scrollbar
			# will not be shown until the selection moves for the first time.
			if attrib == "size":
				size = ensure_str(value)
			elif attrib == "position":
				pos = ensure_str(value)
			elif attrib == "font":
				font = ensure_str(value)
				skinAttributes.append((attrib, font))
			else:
				skinAttributes.append((attrib, ensure_str(value)))
	if pos != None:
		pos, size = context.parse(pos, size, font)
		skinAttributes.append(("position", pos))
	if size != None:
		skinAttributes.append(("size", size))


class AttributeParser:
	def __init__(self, guiObject, desktop, scale=((1, 1), (1, 1))):
		self.guiObject = guiObject
		self.desktop = desktop
		self.scaleTuple = scale

	def applyOne(self, attrib, value):
		try:
			getattr(self, attrib)(value)
		except AttributeError:
			print("[Skin] Attribute '%s' (with value of '%s') in object of type '%s' is not implemented!" % (attrib, value, self.guiObject.__class__.__name__))
		except SkinError as err:
			print("[Skin] Error: %s" % str(err))
		except Exception:
			print("[Skin] Attribute '%s' with wrong (or unknown) value '%s' in object of type '%s'!" % (attrib, value, self.guiObject.__class__.__name__))

	def applyAll(self, attrs):
		attrs.sort(key=lambda a: {"pixmap": 1}.get(a[0], 0))  # For svg pixmap scale required the size, so sort pixmap last
		for attrib, value in attrs:
			self.applyOne(attrib, value)

	def conditional(self, value):
		pass

	def objectTypes(self, value):
		pass

	def position(self, value):
		self.guiObject.move(ePoint(*value) if isinstance(value, tuple) else parsePosition(value, self.scaleTuple, self.guiObject, self.desktop, self.guiObject.csize()))

	def size(self, value):
		self.guiObject.resize(eSize(*value) if isinstance(value, tuple) else parseSize(value, self.scaleTuple, self.guiObject, self.desktop))

	def animationPaused(self, value):
		pass

# OpenPLi is missing the C++ code to support this animation method.
#
# 	def animationMode(self, value):
# 		try:
# 			self.guiObject.setAnimationMode({
# 				"disable": 0x00,
# 				"off": 0x00,
# 				"offshow": 0x10,
# 				"offhide": 0x01,
# 				"onshow": 0x01,
# 				"onhide": 0x10,
# 				"disable_onshow": 0x10,
# 				"disable_onhide": 0x01
# 			}[value])
# 		except KeyError:
# 			print("[Skin] Error: Invalid animationMode '%s'!  Must be one of 'disable', 'off', 'offshow', 'offhide', 'onshow' or 'onhide'." % value)

	def title(self, value):
		self.guiObject.setTitle(_(value))

	def text(self, value):
		self.guiObject.setText(_(value))

	def font(self, value):
		self.guiObject.setFont(parseFont(value, self.scaleTuple))

	def secondfont(self, value):
		self.guiObject.setSecondFont(parseFont(value, self.scaleTuple))

	def zPosition(self, value):
		self.guiObject.setZPosition(int(value))

	def itemHeight(self, value):
		self.guiObject.setItemHeight(parseScale(value))

	def pixmap(self, value):
		if value.endswith(".svg"): # if graphic is svg force alphatest to "blend"
			self.guiObject.setAlphatest(BT_ALPHABLEND)
		self.guiObject.setPixmap(loadPixmap(value, self.desktop, self.guiObject.size().width(), self.guiObject.size().height()))

	def backgroundPixmap(self, value):
		self.guiObject.setBackgroundPicture(loadPixmap(value, self.desktop))

	def selectionPixmap(self, value):
		self.guiObject.setSelectionPicture(loadPixmap(value, self.desktop))

	def sliderPixmap(self, value):
		self.guiObject.setSliderPicture(loadPixmap(value, self.desktop))

	def scrollbarbackgroundPixmap(self, value):
		self.guiObject.setScrollbarBackgroundPicture(loadPixmap(value, self.desktop))

	def scrollbarSliderPicture(self, value):  # For compatibility same as sliderPixmap.
		self.guiObject.setSliderPicture(loadPixmap(value, self.desktop))

	def scrollbarBackgroundPicture(self, value):  # For compatibility same as scrollbarbackgroundPixmap.
		self.guiObject.setScrollbarBackgroundPicture(loadPixmap(value, self.desktop))

	def alphatest(self, value):
		try:
			self.guiObject.setAlphatest({
				"on": BT_ALPHATEST,
				"off": 0,
				"blend": BT_ALPHABLEND
			}[value])
		except KeyError:
			print("[Skin] Error: Invalid alphatest '%s'!  Must be one of 'on', 'off' or 'blend'." % value)

	def scale(self, value):
		value = 1 if value.lower() in ("1", "enabled", "on", "scale", "true", "yes") else 0
		self.guiObject.setScale(value)

	def orientation(self, value):  # Used by eSlider.
		try:
			self.guiObject.setOrientation(*{
				"orVertical": (self.guiObject.orVertical, False),
				"orTopToBottom": (self.guiObject.orVertical, False),
				"orBottomToTop": (self.guiObject.orVertical, True),
				"orHorizontal": (self.guiObject.orHorizontal, False),
				"orLeftToRight": (self.guiObject.orHorizontal, False),
				"orRightToLeft": (self.guiObject.orHorizontal, True)
			}[value])
		except KeyError:
			print("[Skin] Error: Invalid orientation '%s'!  Must be one of 'orVertical', 'orTopToBottom', 'orBottomToTop', 'orHorizontal', 'orLeftToRight' or 'orRightToLeft'." % value)

	def valign(self, value):
		try:
			self.guiObject.setVAlign({
				"top": self.guiObject.alignTop,
				"center": self.guiObject.alignCenter,
				"bottom": self.guiObject.alignBottom
			}[value])
		except KeyError:
			print("[Skin] Error: Invalid valign '%s'!  Must be one of 'top', 'center' or 'bottom'." % value)

	def halign(self, value):
		try:
			self.guiObject.setHAlign({
				"left": self.guiObject.alignLeft,
				"center": self.guiObject.alignCenter,
				"right": self.guiObject.alignRight,
				"block": self.guiObject.alignBlock
			}[value])
		except KeyError:
			print("[Skin] Error: Invalid halign '%s'!  Must be one of 'left', 'center', 'right' or 'block'." % value)

	def textOffset(self, value):
		x, y = value.split(",")
		self.guiObject.setTextOffset(ePoint(int(x) * self.scaleTuple[0][0] // self.scaleTuple[0][1], int(y) * self.scaleTuple[1][0] // self.scaleTuple[1][1]))

	def flags(self, value):
		flags = value.split(",")
		for f in flags:
			try:
				fv = eWindow.__dict__[f]
				self.guiObject.setFlag(fv)
			except KeyError:
				print("[Skin] Error: Invalid flag '%s'!" % f)

	def backgroundColor(self, value):
		self.guiObject.setBackgroundColor(parseColor(value))

	def backgroundColorSelected(self, value):
		self.guiObject.setBackgroundColorSelected(parseColor(value))

	def foregroundColor(self, value):
		self.guiObject.setForegroundColor(parseColor(value))

	def foregroundColorSelected(self, value):
		self.guiObject.setForegroundColorSelected(parseColor(value))

	def foregroundNotCrypted(self, value):
		self.guiObject.setForegroundColor(parseColor(value))

	def backgroundNotCrypted(self, value):
		self.guiObject.setBackgroundColor(parseColor(value))

	def foregroundCrypted(self, value):
		self.guiObject.setForegroundColor(parseColor(value))

	def backgroundCrypted(self, value):
		self.guiObject.setBackgroundColor(parseColor(value))

	def foregroundEncrypted(self, value):
		self.guiObject.setForegroundColor(parseColor(value))

	def backgroundEncrypted(self, value):
		self.guiObject.setBackgroundColor(parseColor(value))

	def shadowColor(self, value):
		self.guiObject.setShadowColor(parseColor(value))

	def selectionDisabled(self, value):
		self.guiObject.setSelectionEnable(0)

	def transparent(self, value):
		self.guiObject.setTransparent(int(value))

	def borderColor(self, value):
		self.guiObject.setBorderColor(parseColor(value))

	def borderWidth(self, value):
		self.guiObject.setBorderWidth(parseScale(value))

	def scrollbarSliderBorderWidth(self, value):
		self.guiObject.setScrollbarSliderBorderWidth(parseScale(value))

	def scrollbarWidth(self, value):
		self.guiObject.setScrollbarWidth(parseScale(value))

	def scrollbarSliderBorderColor(self, value):
		self.guiObject.setSliderBorderColor(parseColor(value))

	def scrollbarSliderForegroundColor(self, value):
		self.guiObject.setSliderForegroundColor(parseColor(value))

	def scrollbarMode(self, value):
		try:
			self.guiObject.setScrollbarMode({
				"showOnDemand": self.guiObject.showOnDemand,
				"showAlways": self.guiObject.showAlways,
				"showNever": self.guiObject.showNever,
				"showLeft": self.guiObject.showLeft
			}[value])
		except KeyError:
			print("[Skin] Error: Invalid scrollbarMode '%s'!  Must be one of 'showOnDemand', 'showAlways', 'showNever' or 'showLeft'." % value)

	def enableWrapAround(self, value):
		value = True if value.lower() in ("1", "enabled", "enablewraparound", "on", "true", "yes") else False
		self.guiObject.setWrapAround(value)

	def pointer(self, value):
		(name, pos) = value.split(":")
		pos = parsePosition(pos, self.scaleTuple)
		ptr = loadPixmap(name, self.desktop)
		self.guiObject.setPointer(0, ptr, pos)

	def seek_pointer(self, value):
		(name, pos) = value.split(":")
		pos = parsePosition(pos, self.scaleTuple)
		ptr = loadPixmap(name, self.desktop)
		self.guiObject.setPointer(1, ptr, pos)

	def shadowOffset(self, value):
		self.guiObject.setShadowOffset(parsePosition(value, self.scaleTuple))

	def noWrap(self, value):
		value = 1 if value.lower() in ("1", "enabled", "nowrap", "on", "true", "yes") else 0
		self.guiObject.setNoWrap(value)

	def split(self, value):
		pass

	def colposition(self, value):
		pass

	def dividechar(self, value):
		pass


def applySingleAttribute(guiObject, desktop, attrib, value, scale=((1, 1), (1, 1))):
	# Is anyone still using applySingleAttribute?
	AttributeParser(guiObject, desktop, scale).applyOne(attrib, value)


def applyAllAttributes(guiObject, desktop, attributes, scale):
	attrs = list(attributes)
	try:
		localAttrs = set(x[0] for x in attrs)
		if hasattr(guiObject, "setScrollbarWidth") and "scrollbarWidth" not in localAttrs:
			attrs.append(("scrollbarWidth", globalScrollbarDefaults["width"]))
		if hasattr(guiObject, "setScrollbarSliderBorderWidth") and "scrollbarSliderBorderWidth" not in localAttrs:
			attrs.append(("scrollbarSliderBorderWidth", globalScrollbarDefaults["borderWidth"]))
		borderColorName = globalScrollbarDefaults.get("borderColorName")
		sliderColorName = globalScrollbarDefaults.get("sliderColorName")
		if hasattr(guiObject, "setSliderBorderColor") and "scrollbarSliderBorderColor" not in localAttrs and borderColorName in colors:
			attrs.append(("scrollbarSliderBorderColor", borderColorName))
		if hasattr(guiObject, "setSliderForegroundColor") and "scrollbarSliderForegroundColor" not in localAttrs and sliderColorName in colors:
			attrs.append(("scrollbarSliderForegroundColor", sliderColorName))
	except Exception:
		pass
	AttributeParser(guiObject, desktop, scale).applyAll(attrs)


def reloadWindowStyles():
	for screenID in windowStyles:
		desktop, screenID, domSkin, pathSkin, scope = windowStyles[screenID]
		loadSingleSkinData(desktop, screenID, domSkin, pathSkin, scope)


def loadSingleSkinData(desktop, screenID, domSkin, pathSkin, scope=SCOPE_CURRENT_SKIN):
	"""Loads skin data like colors, windowstyle etc."""
	assert domSkin.tag == "skin", "root element in skin must be 'skin'!"
	global colors, fonts, menus, parameters, setups, switchPixmap
	for tag in domSkin.findall("output"):
		scrnID = int(tag.attrib.get("id", GUI_SKIN_ID))
		if scrnID == GUI_SKIN_ID:
			for res in tag.findall("resolution"):
				xres = res.attrib.get("xres")
				xres = int(xres) if xres else 720
				yres = res.attrib.get("yres")
				yres = int(yres) if yres else 576
				bpp = res.attrib.get("bpp")
				bpp = int(bpp) if bpp else 32
				# print("[Skin] DEBUG: Resolution xres=%d, yres=%d, bpp=%d." % (xres, yres, bpp))
				from enigma import gMainDC
				gMainDC.getInstance().setResolution(xres, yres)
				desktop.resize(eSize(xres, yres))
				if bpp != 32:
					pass  # Load palette (Not yet implemented!)

				fonts["Body"] = applySkinFactor(*BodyFont)

				# Only add font aliases here for lists that are not part of enigma2 repo.
				# Font aliases for modules in this repository should be dealt with directly in the corresponding py, not here.
				fonts["Dreamexplorer"] = fonts["Body"]
				fonts["ExpandableList"] = fonts["Body"]
				fonts["ImsSelectionList"] = applySkinFactor("Regular", 22, 30)
				fonts["PartnerBoxBouquetList0"] = applySkinFactor("Regular", 20, 30)
				fonts["PartnerBoxBouquetList1"] = applySkinFactor("Regular", 18)
				fonts["PartnerBoxChannelList0"] = applySkinFactor("Regular", 20, 70)
				fonts["PartnerBoxChannelList1"] = applySkinFactor("Regular", 18)
				fonts["PartnerBoxChannelEPGList0"] = applySkinFactor("Regular", 22, 30)
				fonts["PartnerBoxE2TimerMenu0"] = applySkinFactor("Regular", 20, 70)
				fonts["PartnerBoxE2TimerMenu1"] = applySkinFactor("Regular", 18)
				fonts["PartnerBoxEntryList0"] = applySkinFactor("Regular", 20, 30)
				fonts["PartnerBoxEntryList1"] = applySkinFactor("Regular", 18)

				# Only add parameters here for lists that are not part of enigma2 repo.
				# Parameters for modules in this repository should be dealt with directly in the corresponding py, not here.
				parameters["AutotimerListChannels"] = applySkinFactor(2, 40, 3, 21)
				parameters["AutotimerListDays"] = applySkinFactor(1, 26, 3, 17)
				parameters["AutotimerListHasTimespan"] = applySkinFactor(103, 3, 100, 17)
				parameters["AutotimerListIcon"] = applySkinFactor(2, -1, 24, 24)
				parameters["AutotimerListRectypeicon"] = applySkinFactor(26, 3, 20, 20)
				parameters["AutotimerListTimerName"] = applySkinFactor(50, 3, 18, 21)
				parameters["AutotimerListTimespan"] = applySkinFactor(2, 26, 3, 17)
				parameters["DreamexplorerIcon"] = applySkinFactor(12, 3, 20, 20)
				parameters["DreamexplorerName"] = applySkinFactor(40, 2, 1000, 22)
				parameters["ExpandableListCategory"] = applySkinFactor(45, 0, 655, 25)
				parameters["ExpandableListIcon"] = applySkinFactor(5, 0, 30, 25)
				parameters["ExpandableListItem"] = applySkinFactor(80, 3, 620, 25)
				parameters["ExpandableListLock"] = applySkinFactor(45, 1, 25, 24)
				parameters["PartnerBoxBouquetListName"] = applySkinFactor(0, 0, 30)
				parameters["PartnerBoxChannelListName"] = applySkinFactor(0, 0, 30)
				parameters["PartnerBoxChannelListTime"] = applySkinFactor(0, 50, 150, 20)
				parameters["PartnerBoxChannelListTitle"] = applySkinFactor(0, 30, 20)
				parameters["PartnerBoxE1TimerState"] = applySkinFactor(170, 50, 170, 20)
				parameters["PartnerBoxE1TimerTime"] = applySkinFactor(0, 50, 170, 20)
				parameters["PartnerBoxE2TimerIcon"] = applySkinFactor(510, 5, 20, 20)
				parameters["PartnerBoxE2TimerIconRepeat"] = applySkinFactor(510, 30, 20, 20)
				parameters["PartnerBoxE2TimerState"] = applySkinFactor(150, 50, 150, 20)
				parameters["PartnerBoxE2TimerTime"] = applySkinFactor(0, 50, 150, 20)
				parameters["PartnerBoxEntryListName"] = applySkinFactor(5, 0, 150, 25)
				parameters["PartnerBoxEntryListIP"] = applySkinFactor(120, 0, 150, 25)
				parameters["PartnerBoxEntryListPort"] = applySkinFactor(270, 0, 100, 25)
				parameters["PartnerBoxEntryListType"] = applySkinFactor(410, 0, 100, 25)
				parameters["PartnerBoxTimerName"] = applySkinFactor(0, 30, 20)
				parameters["PartnerBoxTimerServicename"] = applySkinFactor(0, 0, 30)
				parameters["SHOUTcastListItem"] = applySkinFactor(20, 18, 22, 69, 20, 23, 43, 22)

	for tag in domSkin.findall("include"):
		filename = tag.attrib.get("filename")
		if filename:
			filename = resolveFilename(scope, filename, path_prefix=pathSkin)
			if isfile(filename):
				loadSkin(filename, scope=scope, desktop=desktop, screenID=screenID)
			else:
				raise SkinError("Included file '%s' not found" % filename)
	for tag in domSkin.findall("switchpixmap"):
		for pixmap in tag.findall("pixmap"):
			name = pixmap.attrib.get("name")
			if not name:
				raise SkinError("Pixmap needs name attribute")
			filename = pixmap.attrib.get("filename")
			if not filename:
				raise SkinError("Pixmap needs filename attribute")
			resolved = resolveFilename(scope, filename, path_prefix=pathSkin)
			if isfile(resolved):
				switchPixmap[name] = LoadPixmap(resolved, cached=True)
			else:
				raise SkinError("The switchpixmap pixmap filename='%s' (%s) not found" % (filename, resolved))
	for tag in domSkin.findall("colors"):
		for color in tag.findall("color"):
			name = color.attrib.get("name")
			color = color.attrib.get("value")
			if name and color:
				colors[name] = parseColor(color)
				# print("[Skin] DEBUG: Color name='%s', color='%s'." % (name, color))
			else:
				raise SkinError("Tag 'color' needs a name and color, got name='%s' and color='%s'" % (name, color))
	for tag in domSkin.findall("fonts"):
		for font in tag.findall("font"):
			filename = font.attrib.get("filename", "<NONAME>")
			name = font.attrib.get("name", "Regular")
			scale = font.attrib.get("scale")
			scale = int(scale) if scale else 100
			isReplacement = font.attrib.get("replacement") and True or False
			render = font.attrib.get("render")
			if render:
				render = int(render)
			else:
				render = 0
			filename = resolveFilename(SCOPE_FONTS, filename, path_prefix=pathSkin)
			filename_emb = resolveFilename(SCOPE_SKIN, filename, path_prefix=pathSkin)
			if isfile(filename):
				addFont(filename, name, scale, isReplacement, render)
				# Log provided by C++ addFont code.
				# print("[Skin] Add font: Font path='%s', name='%s', scale=%d, isReplacement=%s, render=%d." % (filename, name, scale, isReplacement, render))
			elif isfile(filename_emb):
				# emedded fonts
				addFont(filename_emb, name, scale, isReplacement, render)
			else:
				raise SkinError("Font file '%s' not found" % filename)
		fallbackFont = resolveFilename(SCOPE_FONTS, "fallback.font", path_prefix=pathSkin)
		if isfile(fallbackFont):
			addFont(fallbackFont, "Fallback", 100, -1, 0)
		# else:  # As this is optional don't raise an error.
		# 	raise SkinError("Fallback font '%s' not found" % fallbackFont)
		for alias in tag.findall("alias"):
			try:
				name = alias.attrib.get("name")
				font = alias.attrib.get("font")
				size = parseScale(alias.attrib.get("size"))
				height = parseScale(alias.attrib.get("height", size))  # To be calculated some day.
				width = parseScale(alias.attrib.get("width", size))  # To be calculated some day.
				fonts[name] = (font, size, height, width)
				# print("[Skin] Add font alias: name='%s', font='%s', size=%d, height=%s, width=%d." % (name, font, size, height, width))
			except Exception as err:
				raise SkinError("Bad font alias: '%s'" % str(err))
	for tag in domSkin.findall("parameters"):
		for parameter in tag.findall("parameter"):
			try:
				name = parameter.attrib.get("name")
				value = parameter.attrib.get("value")
				parameters[name] = list(map(parseParameter, [x.strip() for x in value.split(",")])) if "," in value else parseParameter(value)
			except Exception as err:
				raise SkinError("Bad parameter: '%s'" % str(err))
	for tag in domSkin.findall("menus"):
		for setup in tag.findall("menu"):
			key = setup.attrib.get("key")
			image = setup.attrib.get("image")
			if key and image:
				menus[key] = image
				# print("[Skin] DEBUG: Menu key='%s', image='%s'." % (key, image))
			else:
				raise SkinError("Tag 'menu' needs key and image, got key='%s' and image='%s'" % (key, image))
	for tag in domSkin.findall("setups"):
		for setup in tag.findall("setup"):
			key = setup.attrib.get("key")
			image = setup.attrib.get("image")
			if key and image:
				setups[key] = image
				# print("[Skin] DEBUG: Setup key='%s', image='%s'." % (key, image))
			else:
				raise SkinError("Tag 'setup' needs key and image, got key='%s' and image='%s'" % (key, image))
	for tag in domSkin.findall("constant-widgets"):
		for constant_widget in tag.findall("constant-widget"):
			name = constant_widget.attrib.get("name")
			if name:
				constantWidgets[name] = constant_widget
	for tag in domSkin.findall("variables"):
		for parameter in tag.findall("variable"):
			name = parameter.attrib.get("name")
			value = parameter.attrib.get("value")
			x, y = value.split(",")
			if value and name:
				variables[name] = "%s,%s" % (str(x), str(y))
	for tag in domSkin.findall("subtitles"):
		from enigma import eSubtitleWidget
		scale = ((1, 1), (1, 1))
		for substyle in tag.findall("sub"):
			font = parseFont(substyle.attrib.get("font"), scale)
			col = substyle.attrib.get("foregroundColor")
			if col:
				foregroundColor = parseColor(col)
				haveColor = 1
			else:
				foregroundColor = gRGB(0xFFFFFF)
				haveColor = 0
			col = substyle.attrib.get("borderColor")
			if col:
				borderColor = parseColor(col)
			else:
				borderColor = gRGB(0)
			borderwidth = substyle.attrib.get("borderWidth")
			if borderwidth is None:
				borderWidth = 3  # Default: Use a subtitle border.
			else:
				borderWidth = int(borderwidth)
			face = eSubtitleWidget.__dict__[substyle.attrib.get("name")]
			eSubtitleWidget.setFontStyle(face, font, haveColor, foregroundColor, borderColor, borderWidth)
	for tag in domSkin.findall("windowstyle"):
		style = eWindowStyleSkinned()
		scrnID = int(tag.attrib.get("id", GUI_SKIN_ID))
		font = gFont("Regular", 20)  # Default
		offset = eSize(20, 5)  # Default
		for title in tag.findall("title"):
			offset = parseSize(title.attrib.get("offset"), ((1, 1), (1, 1)))
			font = parseFont(title.attrib.get("font"), ((1, 1), (1, 1)))
		style.setTitleFont(font)
		style.setTitleOffset(offset)
		# print("[Skin] DEBUG: WindowStyle font, offset - '%s' '%s'." % (str(font), str(offset)))
		for borderset in tag.findall("borderset"):
			bsName = str(borderset.attrib.get("name"))
			for pixmap in borderset.findall("pixmap"):
				bpName = pixmap.attrib.get("pos")
				filename = pixmap.attrib.get("filename")
				if filename and bpName:
					png = loadPixmap(resolveFilename(scope, filename, path_prefix=pathSkin), desktop)
					try:
						style.setPixmap(eWindowStyleSkinned.__dict__[bsName], eWindowStyleSkinned.__dict__[bpName], png)
					except Exception:
						pass
				# print("[Skin] DEBUG: WindowStyle borderset name, filename - '%s' '%s'." % (bpName, filename))
		for color in tag.findall("color"):
			colorType = color.attrib.get("name")
			color = parseColor(color.attrib.get("color"))
			try:
				style.setColor(eWindowStyleSkinned.__dict__["col" + colorType], color)
			except Exception:
				raise SkinError("Unknown color type '%s'" % colorType)
			# print("[Skin] DEBUG: WindowStyle color type, color -" % (colorType, str(color)))
		for scrollbar in tag.findall("scrollbar"):
			offset = int(scrollbar.attrib.get("scrollbarOffset", 5))
			width = int(scrollbar.attrib.get("scrollbarWidth", 20))
			setListBoxScrollbarStyle(width, offset)
		x = eWindowStyleManager.getInstance()
		x.setStyle(scrnID, style)
	for tag in domSkin.findall("margin"):
		scrnID = int(tag.attrib.get("id", GUI_SKIN_ID))
		r = eRect(0, 0, 0, 0)
		v = tag.attrib.get("left")
		if v:
			r.setLeft(int(v))
		v = tag.attrib.get("top")
		if v:
			r.setTop(int(v))
		v = tag.attrib.get("right")
		if v:
			r.setRight(int(v))
		v = tag.attrib.get("bottom")
		if v:
			r.setBottom(int(v))
		# The "desktop" parameter is hard-coded to the GUI screen, so we must ask
		# for the one that this actually applies to.
		getDesktop(scrnID).setMargins(r)


class additionalWidget:
	def __init__(self):
		pass


# Class that makes a tuple look like something else. Some plugins just assume
# that size is a string and try to parse it. This class makes that work.
class SizeTuple(tuple):
	def __str__(self):
		return "%s,%s" % self

	def split(self, *args):
		return str(self[0]), str(self[1])

	def strip(self, *args):
		return "%s,%s" % self

	def __str__(self):
		return "%s,%s" % self


class SkinContext:
	def __init__(self, parent=None, pos=None, size=None, font=None):
		if parent is not None:
			if pos is not None:
				pos, size = parent.parse(pos, size, font)
				self.x, self.y = pos
				self.w, self.h = size
			else:
				self.x = None
				self.y = None
				self.w = None
				self.h = None

	def __str__(self):
		return "Context (%s,%s)+(%s,%s) " % (self.x, self.y, self.w, self.h)

	def parse(self, pos, size, font):
		if size in variables:
			size = variables[size]
		if pos == "fill":
			pos = (self.x, self.y)
			size = (self.w, self.h)
			self.w = 0
			self.h = 0
		else:
			w, h = size.split(",")
			w = parseCoordinate(w, self.w, 0, font)
			h = parseCoordinate(h, self.h, 0, font)
			if pos == "bottom":
				pos = (self.x, self.y + self.h - h)
				size = (self.w, h)
				self.h -= h
			elif pos == "top":
				pos = (self.x, self.y)
				size = (self.w, h)
				self.h -= h
				self.y += h
			elif pos == "left":
				pos = (self.x, self.y)
				size = (w, self.h)
				self.x += w
				self.w -= w
			elif pos == "right":
				pos = (self.x + self.w - w, self.y)
				size = (w, self.h)
				self.w -= w
			else:
				if pos in variables:
					pos = variables[pos]
				size = (w, h)
				pos = pos.split(",")
				pos = (self.x + parseCoordinate(pos[0], self.w, size[0], font), self.y + parseCoordinate(pos[1], self.h, size[1], font))
		return (SizeTuple(pos), SizeTuple(size))


# A context that stacks things instead of aligning them.
#
class SkinContextStack(SkinContext):
	def parse(self, pos, size, font):
		if size in variables:
			size = variables[size]
		if pos == "fill":
			pos = (self.x, self.y)
			size = (self.w, self.h)
		else:
			w, h = size.split(",")
			w = parseCoordinate(w, self.w, 0, font)
			h = parseCoordinate(h, self.h, 0, font)
			if pos == "bottom":
				pos = (self.x, self.y + self.h - h)
				size = (self.w, h)
			elif pos == "top":
				pos = (self.x, self.y)
				size = (self.w, h)
			elif pos == "left":
				pos = (self.x, self.y)
				size = (w, self.h)
			elif pos == "right":
				pos = (self.x + self.w - w, self.y)
				size = (w, self.h)
			else:
				if pos in variables:
					pos = variables[pos]
				size = (w, h)
				pos = pos.split(",")
				pos = (self.x + parseCoordinate(pos[0], self.w, size[0], font), self.y + parseCoordinate(pos[1], self.h, size[1], font))
		return (SizeTuple(pos), SizeTuple(size))


def readSkin(screen, skin, names, desktop):
	if not isinstance(names, list):
		names = [names]
	for n in names:  # Try all skins, first existing one has priority.
		myScreen, path = domScreens.get(n, (None, None))
		if myScreen is not None:
			if screen.mandatoryWidgets is None:
				screen.mandatoryWidgets = []
			else:
				widgets = findWidgets(n)
			if screen.mandatoryWidgets == [] or all(item in widgets for item in screen.mandatoryWidgets):
				name = n  # Use this name for debug output.
				break
			else:
				print("[Skin] Warning: Skin screen '%s' rejected as it does not offer all the mandatory widgets '%s'!" % (n, ", ".join(screen.mandatoryWidgets)))
				myScreen = None
	else:
		name = "<embedded-in-%s>" % screen.__class__.__name__
	if myScreen is None:  # Otherwise try embedded skin.
		myScreen = getattr(screen, "parsedSkin", None)
	if myScreen is None and getattr(screen, "skin", None):  # Try uncompiled embedded skin.
		if isinstance(screen.skin, list):
			print("[Skin] Resizable embedded skin template found in '%s'." % name)
			skin = screen.skin[0] % tuple([int(x * getSkinFactor()) for x in screen.skin[1:]])
		else:
			skin = screen.skin
		print("[Skin] Parsing embedded skin '%s'." % name)
		if isinstance(skin, tuple):
			for s in skin:
				candidate = fromstring(s)
				if candidate.tag == "screen":
					screenID = candidate.attrib.get("id", None)
					if (not screenID) or (int(screenID) == DISPLAY_SKIN_ID):
						myScreen = candidate
						break
			else:
				print("[Skin] No suitable screen found!")
		else:
			myScreen = fromstring(skin)
		if myScreen:
			screen.parsedSkin = myScreen
	if myScreen is None:
		print("[Skin] No skin to read or screen to display.")
		myScreen = screen.parsedSkin = fromstring("<screen></screen>")
	screen.skinAttributes = []
	skinPath = getattr(screen, "skin_path", path)
	context = SkinContextStack()
	s = desktop.bounds()
	context.x = s.left()
	context.y = s.top()
	context.w = s.width()
	context.h = s.height()
	del s
	collectAttributes(screen.skinAttributes, myScreen, context, skinPath, ignore=("name",))
	context = SkinContext(context, myScreen.attrib.get("position"), myScreen.attrib.get("size"))
	screen.additionalWidgets = []
	screen.renderer = []
	usedComponents = set()

	def processConstant(constant_widget, context):
		wname = constant_widget.attrib.get("name")
		if wname:
			try:
				cwvalue = constantWidgets[wname]
			except KeyError:
				raise SkinError("Given constant-widget '%s' not found in skin" % wname)
		if cwvalue:
			for x in cwvalue:
				myScreen.append((x))
		try:
			myScreen.remove(constant_widget)
		except ValueError:
			pass

	def processNone(widget, context):
		pass

	def processWidget(widget, context):
		# Okay, we either have 1:1-mapped widgets ("old style"), or 1:n-mapped
		# widgets (source->renderer).
		wname = widget.attrib.get("name")
		wsource = widget.attrib.get("source")
		wrender = widget.attrib.get("render")
		last_converter_type = ""
		last_converter_args = ""
		if wname is None and wsource is None:
			err = SkinError("The widget has no name and no source")
			_skin_write_widget_error_event("Widget definition error", _skin_make_widget_context(widget), err, False)
			raise err
			return
		if wname:
			# print("[Skin] DEBUG: Widget name='%s'." % wname)
			usedComponents.add(wname)
			try:  # Get corresponding "gui" object.
				attributes = screen[wname].skinAttributes = []
			except Exception:
				err = SkinError("Component with name '%s' was not found in skin of screen '%s'" % (wname, name))
				_skin_write_widget_error_event("Widget component lookup failed", _skin_make_widget_context(widget), err, False)
				raise err
			# assert screen[wname] is not Source
			collectAttributes(attributes, widget, context, skinPath, ignore=("name",))
		elif wsource:
			# print("[Skin] DEBUG: Widget source='%s'." % wsource)
			while True:  # Get corresponding source until we found a non-obsolete source.
				# Parse our current "wsource", which might specify a "related screen" before the dot,
				# for example to reference a parent, global or session-global screen.
				scr = screen
				path = wsource.split(".")  # Resolve all path components.
				while len(path) > 1:
					scr = screen.getRelatedScreen(path[0])
					if scr is None:
						# print("[Skin] DEBUG: wsource='%s', name='%s'." % (wsource, name))
						err = SkinError("Specified related screen '%s' was not found in screen '%s'" % (wsource, name))
						_skin_write_widget_error_event("Widget source screen lookup failed", _skin_make_widget_context(widget), err, False)
						raise err
					path = path[1:]
				source = scr.get(path[0])  # Resolve the source.
				if isinstance(source, ObsoleteSource):
					# If we found an "obsolete source", issue warning, and resolve the real source.
					print("[Skin] WARNING: SKIN '%s' USES OBSOLETE SOURCE '%s', USE '%s' INSTEAD!" % (name, wsource, source.newSource))
					print("[Skin] OBSOLETE SOURCE WILL BE REMOVED %s, PLEASE UPDATE!" % source.removalDate)
					if source.description:
						print("[Skin] Source description: '%s'." % source.description)
					wsource = source.new_source
				else:
					break  # Otherwise, use the source.
			if source is None:
				err = SkinError("The source '%s' was not found in screen '%s'" % (wsource, name))
				_skin_write_widget_error_event("Widget source not found", _skin_make_widget_context(widget), err, False)
				raise err
			if not wrender:
				err = SkinError("For source '%s' a renderer must be defined with a 'render=' attribute" % wsource)
				_skin_write_widget_error_event("Renderer missing for source widget", _skin_make_widget_context(widget), err, False)
				raise err
			for converter in widget.findall("convert"):
				ctype = converter.get("type")
				assert ctype, "[Skin] The 'convert' tag needs a 'type' attribute!"
				# print("[Skin] DEBUG: Converter='%s'." % ctype)
				try:
					parms = converter.text.strip()
				except Exception:
					parms = ""
				last_converter_type = ctype
				last_converter_args = parms
				# print("[Skin] DEBUG: Params='%s'." % parms)
				try:
					converterClass = my_import(".".join(("Components", "Converter", ctype))).__dict__.get(ctype)
				except ImportError:
					err = SkinError("Converter '%s' not found" % ctype)
					_skin_write_widget_error_event("Converter import failed", _skin_make_widget_context(widget, ctype, parms), err, False)
					raise err
				c = None
				for i in source.downstream_elements:
					if isinstance(i, converterClass) and i.converter_arguments == parms:
						c = i
				if c is None:
					try:
						c = converterClass(parms)
						c.connect(source)
					except Exception as err:
						_skin_write_widget_error_event("Converter instantiate/connect failed", _skin_make_widget_context(widget, ctype, parms), err, _skin_helper_verbose())
						raise
				source = c
			try:
				rendererClass = my_import(".".join(("Components", "Renderer", wrender))).__dict__.get(wrender)
			except ImportError:
				err = SkinError("Renderer '%s' not found" % wrender)
				_skin_write_widget_error_event("Renderer import failed", _skin_make_widget_context(widget, last_converter_type, last_converter_args), err, False)
				raise err
			try:
				renderer = rendererClass()  # Instantiate renderer.
				renderer.connect(source)  # Connect to source.
			except Exception as err:
				_skin_write_widget_error_event("Renderer instantiate/connect failed", _skin_make_widget_context(widget, last_converter_type, last_converter_args), err, _skin_helper_verbose())
				raise
			attributes = renderer.skinAttributes = []
			collectAttributes(attributes, widget, context, skinPath, ignore=("render", "source"))
			screen.renderer.append(renderer)

	def processApplet(widget, context):
		try:
			codeText = widget.text.strip()
			widgetType = widget.attrib.get("type")
			code = compile(codeText, "skin applet", "exec")
		except Exception as err:
			raise SkinError("Applet failed to compile: '%s'" % str(err))
		if widgetType == "onLayoutFinish":
			screen.onLayoutFinish.append(code)
		else:
			raise SkinError("Applet type '%s' is unknown" % widgetType)

	def processLabel(widget, context):
		w = additionalWidget()
		w.widget = eLabel
		w.skinAttributes = []
		collectAttributes(w.skinAttributes, widget, context, skinPath, ignore=("name",))
		screen.additionalWidgets.append(w)

	def processPixmap(widget, context):
		w = additionalWidget()
		w.widget = ePixmap
		w.skinAttributes = []
		collectAttributes(w.skinAttributes, widget, context, skinPath, ignore=("name",))
		screen.additionalWidgets.append(w)

	def processScreen(widget, context):
		for w in widget.findall('constant-widget'):
			processConstant(w, context)
		for w in widget:
			conditional = w.attrib.get("conditional")
			if conditional and not [i for i in conditional.split(",") if i in screen.keys()]:
				continue
			objecttypes = w.attrib.get("objectTypes", "").split(",")
			if len(objecttypes) > 1 and (objecttypes[0] not in screen.keys() or not [i for i in objecttypes[1:] if i == screen[objecttypes[0]].__class__.__name__]):
				continue
			includes = w.attrib.get("includes")
			if includes and not [i for i in includes.split(",") if i in screen.keys()]:
				continue
			excludes = w.attrib.get("excludes")
			if excludes and [i for i in excludes.split(",") if i in screen.keys()]:
				continue
			p = processors.get(w.tag, processNone)
			try:
				p(w, context)
			except SkinError as err:
				print("[Skin] Error in screen '%s' widget '%s' %s!" % (name, w.tag, str(err)))

	def processPanel(widget, context):
		n = widget.attrib.get("name")
		if n:
			try:
				s = domScreens[n]
			except KeyError:
				print("[Skin] Error: Unable to find screen '%s' referred in screen '%s'!" % (n, name))
			else:
				processScreen(s[0], context)
		layout = widget.attrib.get("layout")
		if layout == "stack":
			cc = SkinContextStack
		else:
			cc = SkinContext
		try:
			c = cc(context, widget.attrib.get("position"), widget.attrib.get("size"), widget.attrib.get("font"))
		except Exception as err:
			raise SkinError("Failed to create skin context (position='%s', size='%s', font='%s') in context '%s': %s" % (widget.attrib.get("position"), widget.attrib.get("size"), widget.attrib.get("font"), context, err))
		processScreen(widget, c)

	processors = {
		None: processNone,
		"constant-widget": processConstant,
		"widget": processWidget,
		"applet": processApplet,
		"eLabel": processLabel,
		"ePixmap": processPixmap,
		"panel": processPanel
	}

	try:
		msg = " from list '%s'" % ", ".join(names) if len(names) > 1 else ""
		posX = "?" if context.x is None else str(context.x)
		posY = "?" if context.y is None else str(context.y)
		sizeW = "?" if context.w is None else str(context.w)
		sizeH = "?" if context.h is None else str(context.h)
		print("[Skin] Processing screen '%s'%s, position=(%s, %s), size=(%s x %s) for module '%s'." % (name, msg, posX, posY, sizeW, sizeH, screen.__class__.__name__))
		context.x = 0  # Reset offsets, all components are relative to screen coordinates.
		context.y = 0
		processScreen(myScreen, context)
	except Exception as err:
		print("[Skin] Error in screen '%s' %s!" % (name, str(err)))

	from Components.GUIComponent import GUIComponent
	unusedComponents = [x for x in set(screen.keys()) - usedComponents if isinstance(x, GUIComponent)]
	assert not unusedComponents, "[Skin] The following components in '%s' don't have a skin entry: %s" % (name, ", ".join(unusedComponents))
	# This may look pointless, but it unbinds "screen" from the nested scope. A better
	# solution is to avoid the nested scope above and use the context object to pass
	# things around.
	screen = None
	usedComponents = None


def findWidgets(name):
	"""
	Return a set of all the widgets found in a screen. Panels will be expanded
	recursively until all referenced widgets are captured. This code only performs
	a simple scan of the XML and no skin processing is performed.
	"""
	widgetSet = set()
	element, path = domScreens.get(name, (None, None))
	if element is not None:
		widgets = element.findall("widget")
		if widgets is not None:
			for widget in widgets:
				name = widget.get("name", None)
				if name is not None:
					widgetSet.add(name)
				source = widget.get("source", None)
				if source is not None:
					widgetSet.add(source)
		panels = element.findall("panel")
		if panels is not None:
			for panel in panels:
				name = panel.get("name", None)
				if name:
					widgetSet.update(findWidgets(name))
	return widgetSet


def getSkinFactor():
	"""
	Return a scaling factor (float) that can be used to rescale screen displays
	to suit the current resolution of the screen.  The scales are based on a
	default screen resolution of HD (720p).  That is the scale factor for a HD
	screen will be 1.
	"""
	skinfactor = getDesktop(GUI_SKIN_ID).size().height() / 720.0
	# if skinfactor not in [0.8, 1, 1.5, 3, 6]:
	# 	print("[Skin] Warning: Unexpected result for getSkinFactor '%0.4f'!" % skinfactor)
	return skinfactor


def applySkinFactor(*d):
	"""
	Multiply the numeric input by the skin factor
	and return the result as an integer.
	"""
	if len(d) == 1:
		return int(d[0] * getSkinFactor())
	return tuple([int(value * getSkinFactor()) if isinstance(value, (int, float)) else value for value in d])


def findSkinScreen(names):
	"""
	Search the domScreens dictionary to see if any of the screen names provided
	have a skin based screen.  This will allow coders to know if the named
	screen will be skinned by the skin code.  A return of None implies that the
	code must provide its own skin for the screen to be displayed to the user.
	"""
	if not isinstance(names, list):
		names = [names]
	for name in names:  # Try all names given, the first one found is the one that will be used by the skin engine.
		screen, path = domScreens.get(name, (None, None))
		if screen is not None:
			return name
	return None


def dump(x, i=0):
	print(" " * i + str(x))
	try:
		for n in x.childNodes:
			dump(n, i + 1)
	except Exception:
		None


# ======================================================================
# SUPPORT ERROR CONTEXT LOGGER
# runtime helper implementation
# controlled by the switches at the top of this file
# ======================================================================

import os as _skin_os
import sys as _skin_sys
import time as _skin_time
import traceback as _skin_traceback

try:
	from xml.etree.ElementTree import tostring as _skin_tostring
except Exception:
	_skin_tostring = None

try:
	_skin_text_type = unicode
except NameError:
	_skin_text_type = str

_SKIN_DEBUG_LOG_DIR = "/home/root/logs"
_SKIN_DEBUG_LOG_FILE = _skin_os.path.join(_SKIN_DEBUG_LOG_DIR, "error_help.log")
_SKIN_ACTIONMAP_HOOKS_INSTALLED = False
_SKIN_SCREEN_HOOKS_INSTALLED = False
_SKIN_ERROR_SUPPRESS_CACHE = {}
_SKIN_ATTR_CONTEXT = {}
_SKIN_GUI_CONTEXT = {}
_SKIN_XML_FILE_BY_ELEMENT = {}
_SKIN_FILE_LINES_CACHE = {}
_SKIN_READ_STACK = []
_SKIN_RECENT_ERRORS = []
_SKIN_RECENT_SCREENS = []
_SKIN_RECENT_ACTIONS = []
_SKIN_RECENT_KEYS = []


def _skin_to_text(value):
	if value is None:
		return _skin_text_type("")
	if isinstance(value, _skin_text_type):
		return value
	try:
		return value.decode("utf-8", "replace")
	except Exception:
		pass
	try:
		return _skin_text_type(value)
	except Exception:
		try:
			return _skin_text_type(repr(value))
		except Exception:
			return _skin_text_type("<unprintable>")


def _skin_helper_enabled():
	try:
		return bool(SKIN_ERROR_CONTEXT)
	except Exception:
		return True


def _skin_helper_verbose():
	try:
		return bool(SKIN_HELPER_VERBOSE)
	except Exception:
		return False


def _skin_ensure_log_dir():
	try:
		if not _skin_os.path.isdir(_SKIN_DEBUG_LOG_DIR):
			_skin_os.makedirs(_SKIN_DEBUG_LOG_DIR)
	except Exception:
		pass


def _skin_unique_backup_name(prefix, suffix):
	stamp = _skin_time.strftime("%Y%m%d-%H%M%S")
	candidate = _skin_os.path.join(_SKIN_DEBUG_LOG_DIR, "%s%s%s" % (prefix, stamp, suffix))
	index = 1
	while _skin_os.path.exists(candidate):
		candidate = _skin_os.path.join(_SKIN_DEBUG_LOG_DIR, "%s%s_%d%s" % (prefix, stamp, index, suffix))
		index += 1
	return candidate


def _skin_prepare_fresh_log():
	if not _skin_helper_enabled():
		return
	try:
		_skin_ensure_log_dir()
		if _skin_os.path.isfile(_SKIN_DEBUG_LOG_FILE) and _skin_os.path.getsize(_SKIN_DEBUG_LOG_FILE) > 0:
			backup = _skin_unique_backup_name("error_help_", ".log")
			try:
				_skin_os.rename(_SKIN_DEBUG_LOG_FILE, backup)
			except Exception:
				pass
		with open(_SKIN_DEBUG_LOG_FILE, "wb"):
			pass
	except Exception:
		pass


def _skin_append_log_line(channel, message):
	if not _skin_helper_enabled():
		return
	try:
		_skin_ensure_log_dir()
		line = "[%s] %s %s\n" % (_skin_to_text(channel), _skin_time.strftime("%Y-%m-%d %H:%M:%S"), _skin_to_text(message))
		with open(_SKIN_DEBUG_LOG_FILE, "ab") as handle:
			handle.write(line.encode("utf-8", "replace"))
	except Exception:
		pass


def _skin_console(level, message):
	text = "[Skin] %s: %s" % (_skin_to_text(level), _skin_to_text(message))
	try:
		print(text)
	except Exception:
		pass


def _skin_log(level, message, to_console=False):
	_skin_append_log_line(level, message)
	if to_console:
		_skin_console(level, message)


def _skin_register_tree_origin(root, filename):
	try:
		for element in root.iter():
			_SKIN_XML_FILE_BY_ELEMENT[id(element)] = filename
	except Exception:
		pass


def _skin_get_element_file(element, default=None):
	if element is None:
		return default
	return _SKIN_XML_FILE_BY_ELEMENT.get(id(element), default)


def _skin_get_file_lines(filename):
	if not filename or filename.startswith("<embedded"):
		return None
	if filename in _SKIN_FILE_LINES_CACHE:
		return _SKIN_FILE_LINES_CACHE[filename]
	try:
		with open(filename, "r") as handle:
			lines = handle.readlines()
			_SKIN_FILE_LINES_CACHE[filename] = lines
			return lines
	except Exception:
		return None


def _skin_compact_element_text(element):
	if element is None:
		return ""
	tag = _skin_to_text(getattr(element, "tag", "unknown"))
	attrs = getattr(element, "attrib", {}) or {}
	parts = []
	for key in ("name", "source", "render"):
		value = attrs.get(key)
		if value not in (None, ""):
			parts.append('%s="%s"' % (key, _skin_to_text(value)))
	if parts:
		return "<%s %s>" % (tag, " ".join(parts))
	return "<%s>" % tag


def _skin_find_best_line(lines, tokens):
	if not lines:
		return None, None
	for token in tokens:
		if not token:
			continue
		for index, line in enumerate(lines):
			if token in line:
				return index + 1, token
	return None, tokens and tokens[0] or None


def _skin_locator_for_node(node, attrib=None, value=None):
	filename = _skin_get_element_file(node)
	if not filename:
		return "<no file information>"
	if filename.startswith("<embedded"):
		return filename
	lines = _skin_get_file_lines(filename)
	if not lines:
		return filename
	tokens = []
	if attrib is not None and value not in (None, ""):
		tokens.append('%s="%s"' % (attrib, _skin_to_text(value)))
	if node is not None:
		for key in ("name", "source", "render", "position", "size", "font"):
			val = node.attrib.get(key)
			if val:
				tokens.append('%s="%s"' % (key, _skin_to_text(val)))
		if getattr(node, "tag", None):
			tokens.append("<%s" % _skin_to_text(node.tag))
	line, token = _skin_find_best_line(lines, tokens)
	if line is not None:
		if token:
			return "%s:%d token=%s" % (filename, line, token)
		return "%s:%d" % (filename, line)
	return filename


def _skin_xml_parse_error(filename, content, err):
	try:
		line, column = err.position
	except Exception:
		line, column = 0, 0
	_skin_log("ERROR", "XML Parse Error in '%s' at line %s, column %s: %s" % (filename, line, column, err), to_console=True)
	try:
		start = max(0, line - 3)
		end = min(len(content), line + 2)
		for index in range(start, end):
			prefix = ">>" if index + 1 == line else "  "
			text = content[index].replace("\t", " ").rstrip("\n")
			_skin_append_log_line("XML", "%s %04d | %s" % (prefix, index + 1, text))
		_skin_append_log_line("XML", "%s^" % (" " * max(0, column)))
	except Exception:
		pass


def _skin_trim_store(store, limit):
	if len(store) > limit:
		del store[:-limit]


def _skin_remember_screen(message):
	if _SKIN_RECENT_SCREENS and _SKIN_RECENT_SCREENS[-1] == message:
		return
	_SKIN_RECENT_SCREENS.append(message)
	_skin_trim_store(_SKIN_RECENT_SCREENS, 40)
	_skin_append_log_line("SCREEN", message)


def _skin_action_to_key(action):
	action_text = _skin_to_text(action)
	normalized = action_text.replace("-", "_")
	lower = normalized.lower()
	mapping = {
		"ok": "KEY_OK",
		"cancel": "KEY_EXIT",
		"exit": "KEY_EXIT",
		"back": "KEY_BACK",
		"menu": "KEY_MENU",
		"info": "KEY_INFO",
		"epg": "KEY_EPG",
		"red": "KEY_RED",
		"green": "KEY_GREEN",
		"yellow": "KEY_YELLOW",
		"blue": "KEY_BLUE",
		"up": "KEY_UP",
		"down": "KEY_DOWN",
		"left": "KEY_LEFT",
		"right": "KEY_RIGHT",
		"audio": "KEY_AUDIO",
		"subtitle": "KEY_SUBTITLE",
		"text": "KEY_TEXT",
		"tv": "KEY_TV",
		"radio": "KEY_RADIO",
		"power": "KEY_POWER",
		"mute": "KEY_MUTE",
		"volumeup": "KEY_VOLUMEUP",
		"volumedown": "KEY_VOLUMEDOWN",
		"channelup": "KEY_CHANNELUP",
		"channeldown": "KEY_CHANNELDOWN",
		"play": "KEY_PLAY",
		"pause": "KEY_PAUSE",
		"stop": "KEY_STOP",
		"record": "KEY_RECORD",
		"rewind": "KEY_REWIND",
		"fastforward": "KEY_FASTFORWARD",
		"next": "KEY_NEXT",
		"previous": "KEY_PREVIOUS",
		"playpause": "KEY_PLAYPAUSE",
		"help": "KEY_HELP",
		"f1": "KEY_F1",
		"f2": "KEY_F2",
		"f3": "KEY_F3",
		"f4": "KEY_F4",
	}
	suffix = ""
	base = lower
	if lower.endswith("_long"):
		base = lower[:-5]
		suffix = "_LONG"
	if base in mapping:
		return mapping[base] + suffix
	if len(base) == 1 and base.isdigit():
		return "KEY_%s%s" % (base, suffix)
	return "ACTION_%s" % action_text.upper()


def _skin_remember_action(screen_name, context_name, action_name, result=None):
	message = "screen='%s' context='%s' action='%s' result='%s'" % (_skin_to_text(screen_name), _skin_to_text(context_name), _skin_to_text(action_name), _skin_to_text(result))
	if not (_SKIN_RECENT_ACTIONS and _SKIN_RECENT_ACTIONS[-1] == message):
		_SKIN_RECENT_ACTIONS.append(message)
		_skin_trim_store(_SKIN_RECENT_ACTIONS, 80)
		_skin_append_log_line("ACTION", message)
	key_text = "key='%s' action='%s'" % (_skin_action_to_key(action_name), _skin_to_text(action_name))
	if not (_SKIN_RECENT_KEYS and _SKIN_RECENT_KEYS[-1] == key_text):
		_SKIN_RECENT_KEYS.append(key_text)
		_skin_trim_store(_SKIN_RECENT_KEYS, 80)
		_skin_append_log_line("KEY", key_text)


def _skin_last_key_text():
	if not _SKIN_RECENT_KEYS:
		return "<none>"
	return _SKIN_RECENT_KEYS[-1]


def _skin_last_action_text():
	if not _SKIN_RECENT_ACTIONS:
		return "<none>"
	return _SKIN_RECENT_ACTIONS[-1]


def _skin_render_recent_error(item):
	count = item.get("count", 1)
	suffix = " (x%d)" % count if count > 1 else ""
	return "%s %s%s" % (_skin_to_text(item.get("time", "")), _skin_to_text(item.get("message", "")), suffix)


def _skin_remember_error(message, signature):
	now = _skin_time.strftime("%H:%M:%S")
	for item in reversed(_SKIN_RECENT_ERRORS):
		if item.get("signature") == signature:
			item["message"] = _skin_to_text(message)
			item["time"] = now
			item["count"] = item.get("count", 1) + 1
			return
	_SKIN_RECENT_ERRORS.append({"signature": signature, "message": _skin_to_text(message), "time": now, "count": 1})
	_skin_trim_store(_SKIN_RECENT_ERRORS, 40)


def _skin_should_emit_error(signature, window=3.0):
	now = _skin_time.time()
	for key in list(_SKIN_ERROR_SUPPRESS_CACHE.keys()):
		try:
			if now - _SKIN_ERROR_SUPPRESS_CACHE[key] > 60.0:
				del _SKIN_ERROR_SUPPRESS_CACHE[key]
		except Exception:
			pass
	last = _SKIN_ERROR_SUPPRESS_CACHE.get(signature)
	_SKIN_ERROR_SUPPRESS_CACHE[signature] = now
	if last is None:
		return True
	return (now - last) > window


def _skin_dump_recent_context(reason):
	_skin_append_log_line("CONTEXT", "================ %s ================" % _skin_to_text(reason))
	if _SKIN_RECENT_SCREENS:
		_skin_append_log_line("CONTEXT", "Recent screens:")
		for item in _SKIN_RECENT_SCREENS[-8:]:
			_skin_append_log_line("SCREEN", item)
	if _SKIN_RECENT_ACTIONS:
		_skin_append_log_line("CONTEXT", "Recent actions:")
		for item in _SKIN_RECENT_ACTIONS[-8:]:
			_skin_append_log_line("ACTION", item)
	if _SKIN_RECENT_ERRORS:
		_skin_append_log_line("CONTEXT", "Recent skin errors:")
		for item in _SKIN_RECENT_ERRORS[-8:]:
			_skin_append_log_line("ERROR", _skin_render_recent_error(item))


def _skin_attribute_signature(context, attrib, err, kind):
	return "%s|%s|%s|%s|%s|%s" % (
		_skin_to_text(kind),
		_skin_to_text(context.get("screenClass", "")),
		_skin_to_text(context.get("selectedScreen", "")),
		_skin_to_text(context.get("widgetName") or context.get("widgetSource") or context.get("xmlTag") or ""),
		_skin_to_text(attrib),
		_skin_to_text(err)
	)


def _skin_write_attribute_event(title, context, err=None, include_traceback=False):
	_skin_append_log_line("DEBUGMAX", "================ %s ================" % _skin_to_text(title))
	for key in ("screenClass", "screenTitle", "selectedScreen", "widgetName", "widgetSource", "widgetRender", "guiObjectType", "attribute", "attributeRawValue", "attributeLocator", "lastKey", "lastAction"):
		value = context.get(key)
		if value not in (None, ""):
			_skin_append_log_line("DEBUGMAX", "%s=%s" % (key, _skin_to_text(value)))
	if context.get("xmlSnippet"):
		_skin_append_log_line("DEBUGMAX", "xmlSnippet=%s" % _skin_to_text(context.get("xmlSnippet")))
	if err is not None:
		_skin_append_log_line("DEBUGMAX", "exceptionType=%s" % err.__class__.__name__)
		_skin_append_log_line("DEBUGMAX", "exception=%s" % _skin_to_text(err))
		if include_traceback:
			for line in _skin_traceback.format_exc().rstrip().split("\n"):
				_skin_append_log_line("DEBUGMAX", line)



def _skin_write_widget_error_event(title, context, err=None, include_traceback=False):
	_skin_append_log_line("DEBUGMAX", "================ %s ================" % _skin_to_text(title))
	for key in ("screenClass", "screenTitle", "selectedScreen", "widgetName", "widgetSource", "widgetRender", "converterType", "converterArgs", "guiObjectType", "attribute", "attributeRawValue", "attributeLocator", "lastKey", "lastAction"):
		value = context.get(key)
		if value not in (None, ""):
			_skin_append_log_line("DEBUGMAX", "%s=%s" % (key, _skin_to_text(value)))
	if context.get("xmlSnippet"):
		_skin_append_log_line("DEBUGMAX", "xmlSnippet=%s" % _skin_to_text(context.get("xmlSnippet")))
	if err is not None:
		_skin_append_log_line("DEBUGMAX", "exceptionType=%s" % err.__class__.__name__)
		_skin_append_log_line("DEBUGMAX", "exception=%s" % _skin_to_text(err))
		if include_traceback:
			for line in _skin_traceback.format_exc().rstrip().split("\n"):
				_skin_append_log_line("DEBUGMAX", line)


def _skin_make_widget_context(widget, converterType="", converterArgs="", guiObjectType=""):
	current = _SKIN_READ_STACK and _SKIN_READ_STACK[-1] or {}
	widgetName = widget.attrib.get("name")
	widgetSource = widget.attrib.get("source")
	widgetRender = widget.attrib.get("render")
	context = {
		"screenClass": _skin_to_text(current.get("screenClass", "")),
		"screenTitle": _skin_to_text(current.get("screenTitle", "")),
		"selectedScreen": _skin_to_text(current.get("selectedScreen", "")),
		"widgetName": _skin_to_text(widgetName or ""),
		"widgetSource": _skin_to_text(widgetSource or ""),
		"widgetRender": _skin_to_text(widgetRender or ""),
		"converterType": _skin_to_text(converterType or ""),
		"converterArgs": _skin_to_text(converterArgs or ""),
		"guiObjectType": _skin_to_text(guiObjectType or ""),
		"xmlSnippet": _skin_compact_element_text(widget),
		"lastKey": _skin_last_key_text(),
		"lastAction": _skin_last_action_text(),
	}
	context["attributeLocator"] = _skin_locator_for_node(widget)
	return context


def _skin_expand_gui_context(guiObject, attrib, value):
	context = dict(_SKIN_GUI_CONTEXT.get(id(guiObject), {}))
	context["guiObjectType"] = guiObject.__class__.__name__
	context["attribute"] = _skin_to_text(attrib)
	context["attributeRawValue"] = _skin_to_text(value)
	node = context.get("_node")
	context["attributeLocator"] = _skin_locator_for_node(node, attrib, value)
	context["lastKey"] = _skin_last_key_text()
	context["lastAction"] = _skin_last_action_text()
	return context


def _skin_make_attr_context(node, skinPath):
	current = _SKIN_READ_STACK and _SKIN_READ_STACK[-1] or {}
	xml_file = _skin_get_element_file(node, skinPath)
	return {
		"screenClass": _skin_to_text(current.get("screenClass", "")),
		"screenTitle": _skin_to_text(current.get("screenTitle", "")),
		"selectedScreen": _skin_to_text(current.get("selectedScreen", "")),
		"requestedNames": _skin_to_text(current.get("requestedNames", "")),
		"xmlTag": _skin_to_text(getattr(node, "tag", "")),
		"widgetName": _skin_to_text(node is not None and node.attrib.get("name", "") or ""),
		"widgetSource": _skin_to_text(node is not None and node.attrib.get("source", "") or ""),
		"widgetRender": _skin_to_text(node is not None and node.attrib.get("render", "") or ""),
		"xmlFile": _skin_to_text(xml_file or ""),
		"xmlSnippet": _skin_compact_element_text(node),
		"_node": node,
	}


def _skin_preview_selected_screen(screen, names):
	requested = names if isinstance(names, list) else [names]
	selected = ""
	node = None
	path = None
	mandatory = getattr(screen, "mandatoryWidgets", None)
	for name in requested:
		candidate, path = domScreens.get(name, (None, None))
		if candidate is None:
			continue
		if mandatory is None or mandatory == []:
			selected = name
			node = candidate
			break
		try:
			widgets = findWidgets(name)
		except Exception:
			widgets = set()
		if all(item in widgets for item in mandatory):
			selected = name
			node = candidate
			break
	if not selected:
		if getattr(screen, "parsedSkin", None) is not None or getattr(screen, "skin", None):
			selected = "<embedded-in-%s>" % screen.__class__.__name__
			node = getattr(screen, "parsedSkin", None)
			path = getattr(screen, "skin_path", path)
	return requested, selected, node, path


def _skin_install_actionmap_hooks():
	global _SKIN_ACTIONMAP_HOOKS_INSTALLED
	if _SKIN_ACTIONMAP_HOOKS_INSTALLED:
		return
	try:
		import Components.ActionMap as _SkinActionMapModule
	except Exception as err:
		_skin_log("WARNING", "Unable to install ActionMap hooks: %s" % err)
		return
	if getattr(_SkinActionMapModule, "_skin_helper_safe_hooked", False):
		_SKIN_ACTIONMAP_HOOKS_INSTALLED = True
		return
	if hasattr(_SkinActionMapModule, "ActionMap") and hasattr(_SkinActionMapModule.ActionMap, "action"):
		_original_action = _SkinActionMapModule.ActionMap.action
		def _safe_action(self, contexts, action):
			parent = getattr(self, "parent", None)
			screen_name = parent is not None and parent.__class__.__name__ or "<none>"
			result = _original_action(self, contexts, action)
			if _skin_helper_enabled():
				_skin_remember_action(screen_name, contexts, action, result)
			return result
		_SkinActionMapModule.ActionMap.action = _safe_action
	if hasattr(_SkinActionMapModule, "NumberActionMap") and hasattr(_SkinActionMapModule.NumberActionMap, "action"):
		_original_number_action = _SkinActionMapModule.NumberActionMap.action
		def _safe_number_action(self, contexts, action):
			parent = getattr(self, "parent", None)
			screen_name = parent is not None and parent.__class__.__name__ or "<none>"
			result = _original_number_action(self, contexts, action)
			if _skin_helper_enabled():
				_skin_remember_action(screen_name, contexts, action, result)
			return result
		_SkinActionMapModule.NumberActionMap.action = _safe_number_action
	_SkinActionMapModule._skin_helper_safe_hooked = True
	_SKIN_ACTIONMAP_HOOKS_INSTALLED = True
	_skin_log("SESSION", "Safe ActionMap debug hooks installed")


def _skin_install_screen_hooks():
	global _SKIN_SCREEN_HOOKS_INSTALLED
	if _SKIN_SCREEN_HOOKS_INSTALLED:
		return
	try:
		from Screens.Screen import Screen as _SkinScreenClass
	except Exception as err:
		_skin_log("WARNING", "Unable to install Screen hooks: %s" % err)
		return
	if getattr(_SkinScreenClass, "_skin_helper_safe_hooked", False):
		_SKIN_SCREEN_HOOKS_INSTALLED = True
		return
	_original_execBegin = _SkinScreenClass.execBegin
	_original_doClose = _SkinScreenClass.doClose
	_original_applySkin = _SkinScreenClass.applySkin
	def _safe_execBegin(self, *args, **kwargs):
		if _skin_helper_enabled():
			try:
				title = self.getTitle()
			except Exception:
				title = ""
			_skin_remember_screen("execBegin class='%s' title='%s' skinName='%s'" % (self.__class__.__name__, _skin_to_text(title), _skin_to_text(getattr(self, "skinName", ""))))
		return _original_execBegin(self, *args, **kwargs)
	def _safe_doClose(self, *args, **kwargs):
		if _skin_helper_enabled():
			try:
				title = self.getTitle()
			except Exception:
				title = ""
			_skin_remember_screen("doClose class='%s' title='%s' skinName='%s'" % (self.__class__.__name__, _skin_to_text(title), _skin_to_text(getattr(self, "skinName", ""))))
		return _original_doClose(self, *args, **kwargs)
	def _safe_applySkin(self, *args, **kwargs):
		if _skin_helper_enabled():
			try:
				title = self.getTitle()
			except Exception:
				title = ""
			_skin_remember_screen("applySkin class='%s' title='%s' skinName='%s'" % (self.__class__.__name__, _skin_to_text(title), _skin_to_text(getattr(self, "skinName", ""))))
		return _original_applySkin(self, *args, **kwargs)
	_SkinScreenClass.execBegin = _safe_execBegin
	_SkinScreenClass.doClose = _safe_doClose
	_SkinScreenClass.applySkin = _safe_applySkin
	_SkinScreenClass._skin_helper_safe_hooked = True
	_SKIN_SCREEN_HOOKS_INSTALLED = True
	_skin_log("SESSION", "Safe Screen hooks installed")


def _skin_install_exception_hook():
	try:
		_original_excepthook = getattr(_skin_install_exception_hook, "_original", None)
		if _original_excepthook is None:
			_skin_install_exception_hook._original = getattr(_skin_sys, "excepthook", None)
			_original_excepthook = _skin_install_exception_hook._original
		def _safe_excepthook(exc_type, exc_value, exc_tb):
			if _skin_helper_enabled():
				_skin_append_log_line("EXCEPTION", "Unhandled Python exception: %s: %s" % (getattr(exc_type, "__name__", exc_type), _skin_to_text(exc_value)))
				for line in _skin_traceback.format_exception(exc_type, exc_value, exc_tb):
					for subline in _skin_to_text(line).rstrip().split("\n"):
						_skin_append_log_line("EXCEPTION", subline)
				_skin_dump_recent_context("Unhandled Python exception")
			if _original_excepthook and _original_excepthook != _safe_excepthook:
				return _original_excepthook(exc_type, exc_value, exc_tb)
		_skin_sys.excepthook = _safe_excepthook
	except Exception:
		pass


def installRuntimeDebugHooks():
	if not _skin_helper_enabled():
		return
	_skin_install_exception_hook()
	_skin_install_screen_hooks()
	# Intentionally no ActionMap hook here.
	# SKIN_DEEP_PLUGIN_DEBUG stays as a visible top-level switch,
	# but it no longer installs runtime key/action wrappers.


_ORIGINAL_removeCallback = removeCallback
_ORIGINAL_collectAttributes = collectAttributes
_ORIGINAL_applyAllAttributes = applyAllAttributes
_ORIGINAL_readSkin = readSkin
_ORIGINAL_loadSkin = loadSkin
_ORIGINAL_reloadSkins = reloadSkins
_ORIGINAL_restoreSkin = restoreSkin
_ORIGINAL_parseColor = parseColor
_ORIGINAL_parseFont = parseFont


def removeCallback(callback):
	if callback in callbacks:
		callbacks.remove(callback)


def restoreSkin():
	try:
		return _ORIGINAL_restoreSkin()
	except Exception:
		_skin_log("ERROR", "restoreSkin failed", to_console=True)
		if _skin_helper_verbose():
			for line in _skin_traceback.format_exc().rstrip().split("\n"):
				_skin_append_log_line("DEBUGMAX", line)


def InitSkins():
	global currentPrimarySkin, currentDisplaySkin, currentStandbySkin, runCallbacks
	installRuntimeDebugHooks()
	runCallbacks = False
	loadSkin(EMERGENCY_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	loadSkin(SUBTITLE_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	if BoxInfo.getItem("OledDisplay"):
		result = []
		for skin, name in [(config.skin.display_skin.value, "current"), (DEFAULT_DISPLAY_SKIN, "default")]:
			if skin in result:
				continue
			config.skin.display_skin.value = skin
			if loadSkin(config.skin.display_skin.value, scope=SCOPE_CURRENT_LCDSKIN, desktop=getDesktop(DISPLAY_SKIN_ID), screenID=DISPLAY_SKIN_ID):
				currentDisplaySkin = config.skin.display_skin.value
				break
			result.append(skin)
		result = []
		for skin, name in [(config.skin.standby_skin.value, "current"), (DEFAULT_STANDBY_SKIN, "default")]:
			if skin in result:
				continue
			config.skin.standby_skin.value = skin
			if loadSkin(config.skin.standby_skin.value, scope=SCOPE_CURRENT_LCDSKIN, desktop=getDesktop(DISPLAY_SKIN_ID), screenID=DISPLAY_SKIN_ID):
				currentStandbySkin = config.skin.standby_skin.value
				break
			result.append(skin)
	result = []
	for skin, name in [(config.skin.primary_skin.value, "current"), (DEFAULT_SKIN, "default")]:
		if skin in result:
			continue
		config.skin.primary_skin.value = skin
		if loadSkin(config.skin.primary_skin.value, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID):
			currentPrimarySkin = config.skin.primary_skin.value
			break
		result.append(skin)
	if currentPrimarySkin is not None:
		partsDir = resolveFilename(SCOPE_GUISKIN, pathjoin(dirname(currentPrimarySkin), "mySkin", ""))
		if pathExists(partsDir) and currentPrimarySkin != DEFAULT_SKIN:
			for file in sorted(listdir(partsDir)):
				if file.startswith("skin_") and file.endswith(".xml"):
					partsFile = pathjoin(partsDir, file)
					loadSkin(partsFile, scope=SCOPE_GUISKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	result = None
	if isfile(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)):
		name = USER_SKIN_TEMPLATE % dirname(config.skin.primary_skin.value)
		if isfile(resolveFilename(SCOPE_CURRENT_SKIN, name)):
			result = loadSkin(name, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	if result is None:
		loadSkin(USER_SKIN, scope=SCOPE_CURRENT_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID)
	runCallbacks = True


def loadSkinData(desktop):
	if _skin_helper_enabled():
		_skin_append_log_line("SESSION", "============================================================")
		_skin_append_log_line("SESSION", "skin.py loadSkinData started")
		_skin_append_log_line("SESSION", "Primary skin setting: %s" % _skin_to_text(getattr(config.skin.primary_skin, "value", "<unknown>")))
	restoreSkin()
	InitSkins()


def loadSkin(filename, scope=SCOPE_SKIN, desktop=getDesktop(GUI_SKIN_ID), screenID=GUI_SKIN_ID):
	global windowStyles
	filename = resolveFilename(scope, filename)
	try:
		with open(filename, "r") as fd:
			try:
				domSkin = parse(fd).getroot()
				_skin_register_tree_origin(domSkin, filename)
				loadSingleSkinData(desktop, screenID, domSkin, filename, scope=scope)
				for element in domSkin:
					if element.tag == "screen":
						name = element.attrib.get("name", None)
						if name:
							scrnID = element.attrib.get("id", None)
							if scrnID is None or int(scrnID) == int(screenID):
								domScreens[name] = (element, "%s/" % dirname(filename))
					elif element.tag == "windowstyle":
						scrnID = element.attrib.get("id", None)
						if scrnID is not None:
							scrnID = int(scrnID)
							domStyle = ElementTree(Element("skin"))
							domStyle.getroot().append(element)
							windowStyles[scrnID] = (desktop, screenID, domStyle.getroot(), filename, scope)
				reloadWindowStyles()
				if runCallbacks:
					for method in callbacks[:]:
						if method:
							try:
								method()
							except Exception:
								_skin_log("ERROR", "Skin callback failed after loading '%s'" % filename, to_console=True)
				return True
			except ParseError as err:
				fd.seek(0)
				content = fd.readlines()
				_skin_xml_parse_error(filename, content, err)
			except Exception as err:
				_skin_log("ERROR", "Unable to parse skin data in '%s' - '%s'" % (filename, err), to_console=True)
				if _skin_helper_verbose():
					for line in _skin_traceback.format_exc().rstrip().split("\n"):
						_skin_append_log_line("DEBUGMAX", line)
	except (IOError, OSError) as err:
		if err.errno == ENOENT:
			_skin_log("WARNING", "Skin file '%s' does not exist" % filename, to_console=True)
		else:
			_skin_log("ERROR", "Opening skin file '%s' failed (%s)" % (filename, err), to_console=True)
	except Exception as err:
		_skin_log("ERROR", "Unexpected error opening skin file '%s' (%s)" % (filename, err), to_console=True)
	return False


def reloadSkins():
	global colors, fonts, currentPrimarySkin, currentDisplaySkin, currentStandbySkin
	domScreens.clear()
	colors.clear()
	colors = {
		"key_back": gRGB(0x00313131),
		"key_blue": gRGB(0x0018188b),
		"key_green": gRGB(0x001f771f),
		"key_red": gRGB(0x009f1313),
		"key_text": gRGB(0x00ffffff),
		"key_yellow": gRGB(0x00a08500)
	}
	fonts.clear()
	fonts = {
		"Body": BodyFont
	}
	menus.clear()
	parameters.clear()
	setups.clear()
	switchPixmap.clear()
	windowStyles.clear()
	constantWidgets.clear()
	variables.clear()
	currentPrimarySkin = None
	currentDisplaySkin = None
	currentStandbySkin = None
	InitSkins()


def collectAttributes(skinAttributes, node, context, skinPath=None, ignore=(), filenames=frozenset(("pixmap", "pointer", "seek_pointer", "backgroundPixmap", "selectionPixmap", "sliderPixmap", "scrollbarSliderPicture", "scrollbarbackgroundPixmap", "scrollbarBackgroundPicture"))):
	result = _ORIGINAL_collectAttributes(skinAttributes, node, context, skinPath, ignore, filenames)
	if _skin_helper_enabled():
		try:
			_SKIN_ATTR_CONTEXT[id(skinAttributes)] = _skin_make_attr_context(node, skinPath)
		except Exception:
			pass
	return result


def applyAllAttributes(guiObject, desktop, attributes, scale):
	if not _skin_helper_enabled():
		return _ORIGINAL_applyAllAttributes(guiObject, desktop, attributes, scale)
	try:
		context = dict(_SKIN_ATTR_CONTEXT.get(id(attributes), {}))
		_SKIN_GUI_CONTEXT[id(guiObject)] = context
		return _ORIGINAL_applyAllAttributes(guiObject, desktop, attributes, scale)
	finally:
		try:
			del _SKIN_GUI_CONTEXT[id(guiObject)]
		except Exception:
			pass


def readSkin(screen, skin, names, desktop):
	if not _skin_helper_enabled():
		return _ORIGINAL_readSkin(screen, skin, names, desktop)
	requested, selected, node, path = _skin_preview_selected_screen(screen, names)
	try:
		title = screen.getTitle()
	except Exception:
		title = ""
	ctx = {
		"screenClass": screen.__class__.__name__,
		"screenTitle": _skin_to_text(title),
		"requestedNames": requested,
		"selectedScreen": selected,
		"screenNode": node,
		"path": path,
	}
	_SKIN_READ_STACK.append(ctx)
	_skin_remember_screen("readSkin class='%s' title='%s' selected='%s' names='%s'" % (screen.__class__.__name__, _skin_to_text(title), _skin_to_text(selected), _skin_to_text(requested)))
	try:
		return _ORIGINAL_readSkin(screen, skin, names, desktop)
	except Exception as err:
		_skin_log("ERROR", "readSkin failed for '%s': %s" % (screen.__class__.__name__, err), to_console=True)
		if _skin_helper_verbose():
			for line in _skin_traceback.format_exc().rstrip().split("\n"):
				_skin_append_log_line("DEBUGMAX", line)
		_skin_dump_recent_context("readSkin exception")
		raise
	finally:
		try:
			_SKIN_READ_STACK.pop()
		except Exception:
			pass


def parseColor(s):
	try:
		return _ORIGINAL_parseColor(s)
	except Exception as err:
		_skin_log("ERROR", "Color '%s' is invalid (%s)" % (_skin_to_text(s), err), to_console=True)
		raise


def parseFont(s, scale=((1, 1), (1, 1))):
	try:
		return _ORIGINAL_parseFont(s, scale)
	except Exception as err:
		_skin_log("ERROR", "Font '%s' could not be parsed (%s)" % (_skin_to_text(s), err), to_console=True)
		raise


def _skin_parse_padding_values(value):
	parts = [parseScale(x.strip()) for x in _skin_to_text(value).split(",")]
	if len(parts) == 1:
		parts = parts * 4
	elif len(parts) == 2:
		parts = [parts[0], parts[1], parts[0], parts[1]]
	elif len(parts) != 4:
		raise SkinError("Attribute 'padding' must have 1, 2 or 4 values")
	return parts


def _skin_scale_h(parser, value):
	return int(value) * parser.scaleTuple[0][0] // parser.scaleTuple[0][1]


def _skin_scale_v(parser, value):
	return int(value) * parser.scaleTuple[1][0] // parser.scaleTuple[1][1]


def _skin_attr_color(self, value):
	if hasattr(self.guiObject, "setForegroundColor"):
		self.guiObject.setForegroundColor(parseColor(value))
	else:
		raise SkinError("Object type '%s' does not support color/foregroundColor" % self.guiObject.__class__.__name__)


def _skin_attr_padding(self, value):
	leftPadding, topPadding, rightPadding, bottomPadding = _skin_parse_padding_values(value)
	if hasattr(self.guiObject, "setPadding"):
		self.guiObject.setPadding(eRect(_skin_scale_h(self, leftPadding), _skin_scale_v(self, topPadding), _skin_scale_h(self, rightPadding), _skin_scale_v(self, bottomPadding)))
	else:
		raise SkinError("Object type '%s' does not support padding" % self.guiObject.__class__.__name__)


def _skin_attr_foregroundColorSelected(self, value):
	color = parseColor(value)
	if hasattr(self.guiObject, "setForegroundColorSelected"):
		self.guiObject.setForegroundColorSelected(color)
	elif hasattr(self.guiObject, "setForegroundColor"):
		self.guiObject.setForegroundColor(color)
	else:
		raise SkinError("Object type '%s' does not support foregroundColorSelected" % self.guiObject.__class__.__name__)


def _skin_attr_backgroundColorSelected(self, value):
	color = parseColor(value)
	if hasattr(self.guiObject, "setBackgroundColorSelected"):
		self.guiObject.setBackgroundColorSelected(color)
	elif hasattr(self.guiObject, "setBackgroundColor"):
		self.guiObject.setBackgroundColor(color)
	else:
		raise SkinError("Object type '%s' does not support backgroundColorSelected" % self.guiObject.__class__.__name__)


def _skin_attr_scrollbarBackgroundPixmap(self, value):
	if hasattr(self.guiObject, "setScrollbarBackgroundPicture"):
		self.guiObject.setScrollbarBackgroundPicture(loadPixmap(value, self.desktop))
	else:
		raise SkinError("Object type '%s' does not support scrollbarBackgroundPixmap" % self.guiObject.__class__.__name__)


def _skin_attr_scrollbarForegroundPixmap(self, value):
	if hasattr(self.guiObject, "setSliderPicture"):
		self.guiObject.setSliderPicture(loadPixmap(value, self.desktop))
	else:
		raise SkinError("Object type '%s' does not support scrollbarForegroundPixmap" % self.guiObject.__class__.__name__)


def _skin_attr_scrollbarBorderColor(self, value):
	if hasattr(self.guiObject, "setSliderBorderColor"):
		self.guiObject.setSliderBorderColor(parseColor(value))
	elif hasattr(self.guiObject, "setScrollbarBorderColor"):
		self.guiObject.setScrollbarBorderColor(parseColor(value))
	else:
		raise SkinError("Object type '%s' does not support scrollbarBorderColor" % self.guiObject.__class__.__name__)


def _skin_attr_scrollbarBorderWidth(self, value):
	if hasattr(self.guiObject, "setScrollbarSliderBorderWidth"):
		self.guiObject.setScrollbarSliderBorderWidth(parseScale(value))
	elif hasattr(self.guiObject, "setScrollbarBorderWidth"):
		self.guiObject.setScrollbarBorderWidth(parseScale(value))
	else:
		raise SkinError("Object type '%s' does not support scrollbarBorderWidth" % self.guiObject.__class__.__name__)


def _skin_attr_scrollbarForegroundColor(self, value):
	if hasattr(self.guiObject, "setSliderForegroundColor"):
		self.guiObject.setSliderForegroundColor(parseColor(value))
	elif hasattr(self.guiObject, "setScrollbarForegroundColor"):
		self.guiObject.setScrollbarForegroundColor(parseColor(value))
	else:
		raise SkinError("Object type '%s' does not support scrollbarForegroundColor" % self.guiObject.__class__.__name__)


def _skin_attr_fieldMargins(self, value):
	for name in ("setFieldMargins", "setfieldMargins"):
		if hasattr(self.guiObject, name):
			return getattr(self.guiObject, name)(parseScale(value))
	if hasattr(self.guiObject, "setMargins"):
		return self.guiObject.setMargins(parseScale(value))
	raise SkinError("Object type '%s' does not support fieldMargins" % self.guiObject.__class__.__name__)


def _skin_attr_itemsDistances(self, value):
	for name in ("setItemsDistances", "setItemDistances"):
		if hasattr(self.guiObject, name):
			return getattr(self.guiObject, name)(parseScale(value))
	raise SkinError("Object type '%s' does not support itemsDistances" % self.guiObject.__class__.__name__)


def _skin_attr_nonplayableMargins(self, value):
	for name in ("setNonplayableMargins", "setNonPlayableMargins"):
		if hasattr(self.guiObject, name):
			return getattr(self.guiObject, name)(parseScale(value))
	raise SkinError("Object type '%s' does not support nonplayableMargins" % self.guiObject.__class__.__name__)


def _skin_attr_progressBarWidth(self, value):
	for name in ("setProgressBarWidth", "setProgressbarWidth"):
		if hasattr(self.guiObject, name):
			return getattr(self.guiObject, name)(parseScale(value))
	raise SkinError("Object type '%s' does not support progressBarWidth" % self.guiObject.__class__.__name__)


def _skin_attr_colorServiceRecording(self, value):
	for name in ("setColorServiceRecording", "setColourServiceRecording"):
		if hasattr(self.guiObject, name):
			return getattr(self.guiObject, name)(parseColor(value))
	raise SkinError("Object type '%s' does not support colorServiceRecording" % self.guiObject.__class__.__name__)


def _skin_applyOne(self, attrib, value):
	if not _skin_helper_enabled():
		return AttributeParser._skin_helper_original_applyOne(self, attrib, value)
	context = _skin_expand_gui_context(self.guiObject, attrib, value)
	try:
		handler = getattr(self, attrib)
	except AttributeError:
		signature = _skin_attribute_signature(context, attrib, "not-implemented", "not-implemented")
		_skin_remember_error("Attribute '%s' not implemented" % attrib, signature)
		if _skin_should_emit_error(signature):
			_skin_write_attribute_event("Attribute not implemented", context, None, False)
		return
	try:
		handler(value)
	except SkinError as err:
		signature = _skin_attribute_signature(context, attrib, err, "skinerror")
		_skin_remember_error("Attribute '%s' skin error" % attrib, signature)
		if _skin_should_emit_error(signature):
			_skin_write_attribute_event("SkinError while applying attribute", context, err, _skin_helper_verbose())
	except Exception as err:
		text = _skin_to_text(err)
		title = "Unsupported attribute on GUI object" if isinstance(err, AttributeError) and "has no attribute 'set" in text else "Attribute crashed"
		signature = _skin_attribute_signature(context, attrib, err, title)
		_skin_remember_error("Attribute '%s' crashed" % attrib, signature)
		if _skin_should_emit_error(signature):
			_skin_write_attribute_event(title, context, err, _skin_helper_verbose())


AttributeParser._skin_helper_original_applyOne = AttributeParser.applyOne
AttributeParser.applyOne = _skin_applyOne
AttributeParser.color = _skin_attr_color
AttributeParser.padding = _skin_attr_padding
AttributeParser.foregroundColorSelected = _skin_attr_foregroundColorSelected
AttributeParser.backgroundColorSelected = _skin_attr_backgroundColorSelected
AttributeParser.scrollbarBackgroundPixmap = _skin_attr_scrollbarBackgroundPixmap
AttributeParser.scrollbarForegroundPixmap = _skin_attr_scrollbarForegroundPixmap
AttributeParser.scrollbarBorderColor = _skin_attr_scrollbarBorderColor
AttributeParser.scrollbarBorderWidth = _skin_attr_scrollbarBorderWidth
AttributeParser.scrollbarForegroundColor = _skin_attr_scrollbarForegroundColor
AttributeParser.fieldMargins = _skin_attr_fieldMargins
AttributeParser.itemsDistances = _skin_attr_itemsDistances
AttributeParser.nonplayableMargins = _skin_attr_nonplayableMargins
AttributeParser.progressBarWidth = _skin_attr_progressBarWidth
AttributeParser.colorServiceRecording = _skin_attr_colorServiceRecording


_skin_prepare_fresh_log()
_skin_append_log_line("SESSION", "skin.py imported and support error context logger initialized")
_skin_append_log_line("SESSION", "Active log file: %s" % _SKIN_DEBUG_LOG_FILE)
_skin_append_log_line("SESSION", "SKIN_ERROR_CONTEXT=%s" % _skin_to_text(SKIN_ERROR_CONTEXT))
_skin_append_log_line("SESSION", "SKIN_HELPER_VERBOSE=%s" % _skin_to_text(SKIN_HELPER_VERBOSE))
_skin_append_log_line("SESSION", "SKIN_DEEP_PLUGIN_DEBUG=%s" % _skin_to_text(SKIN_DEEP_PLUGIN_DEBUG))
if bool(globals().get("SKIN_DEEP_PLUGIN_DEBUG", False)):
	_skin_append_log_line("SESSION", "SKIN_DEEP_PLUGIN_DEBUG is ON (safe mode, no ActionMap hook)")
else:
	_skin_append_log_line("SESSION", "SKIN_DEEP_PLUGIN_DEBUG is OFF (safe mode, no ActionMap hook)")
