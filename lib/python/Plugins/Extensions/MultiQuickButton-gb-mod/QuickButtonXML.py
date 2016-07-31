# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

import xml.dom.minidom
from xml.dom import minidom, Node
from Tools.XMLTools import stringToXML
from __init__ import _

functionfile = "/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/mqbfunctions.xml"

class QuickButtonXML(object):
	
	def __init__(self, menu=None):
		
		if menu:
			self.rootNode = menu.childNodes[0]
			self.list = []
			self.list = self.getEntry()
		else:
			self.list = []

	def getEntry(self):
		mnulist = []
		for node in self.rootNode.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				for node2 in node.childNodes:
					if node2.nodeType == Node.ELEMENT_NODE:
						name = screen = code = module = sel =""
						for node3 in node2.childNodes:
							if node2.nodeType == Node.ELEMENT_NODE:
								for node4 in node3.childNodes:
									if node3.nodeType == Node.ELEMENT_NODE:
										if node4.nodeType == Node.TEXT_NODE:
											if node3.nodeName == "name":
												name = node4.nodeValue.encode('utf-8')
											elif node3.nodeName == "sel":
												sel = node4.nodeValue.encode('utf-8')
											elif node3.nodeName == "module":
												module = node4.nodeValue.encode('utf-8')
										elif node4.nodeType == Node.CDATA_SECTION_NODE:
											if node3.nodeName == "screen":
												screen = node4.wholeText.encode('utf-8')
											elif node3.nodeName == "code":
												code = node4.wholeText.encode('utf-8')
						category = node.nodeName.encode('utf-8')
						mnulist.append((name, sel, category, module, screen, code))
				mnulist.append(("--", "", "", "", "", ""))
		return mnulist[:(len(mnulist)-1)]
	def getMenu(self):
		return self.list

	def getSelection(self):
		selection = []
		if self.list <> []:
			for i in self.list:
				if i[1] == "1":
					selection.append((i))
			return selection

	def setSelection(self, name, sel):
		selection = []
		if self.list <> []:
			for i in self.list:
				if i[0] == name:
					selection.append((i[0], sel, i[2], i[3], i[4], i[5]))
				else:
					selection.append((i))
			self.list = selection
		return self.list

	def rmEntry(self, name):
		selection = []
		if self.list <> []:
			for i in self.list:
				if i[0] == name:
					pass
				else:
					selection.append((i))
			self.list = selection
		return self.list

	def addPluginEntry(self, name):
		if name <> None:
			code = "\nfor plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):\n	if plugin.name == _(\""+ name + "\"):\n		runPlugin(self, plugin)\n		break\n"
		else:
			return ""
		idx = 0
		if self.list <> []:
			for i in self.list:
				if i[2] == "Menu":
					idx += 1
				elif i[2] == "Plugins":
					idx += 1
				else:
					pass
			if idx > 0:
				idx +=1
			else:
				pass
			tmp = self.list[:idx]
			tmp.append((name, "1", "Menu", "", "", code))
			tmp += self.list[idx:]
			self.list = tmp
		else:
			self.list = []
			self.list.append((name, "1", "Menu", "", "", code))
		return self.list

	def addFunctionEntry(self, name):
		if name <> None:
			functionname = name
			mqbfunctionfile = functionfile
			self.mqbfunctions = xml.dom.minidom.parse(mqbfunctionfile)
			for mqbfunction in self.mqbfunctions.getElementsByTagName("mqbfunction"):
				if str(mqbfunction.getElementsByTagName("name")[0].childNodes[0].data) == functionname:
					if mqbfunction.getElementsByTagName("module"):
						module = str(mqbfunction.getElementsByTagName("module")[0].childNodes[0].data)
					else:
						module = ""
					if mqbfunction.getElementsByTagName("screen"):
						screen = str(mqbfunction.getElementsByTagName("screen")[0].childNodes[0].data)
					else:
						screen = ""
					if mqbfunction.getElementsByTagName("code"):
						code = str(mqbfunction.getElementsByTagName("code")[0].childNodes[0].data)
					else:
						code = ""
		else:
			return ""
		idx = 0
		if self.list <> []:
			for i in self.list:
				if i[2] == "Menu":
					idx += 1
				elif i[2] == "Plugins":
					idx += 1
				else:
					pass
			if idx > 0:
				idx +=1
			else:
				pass
			tmp = self.list[:idx]
			tmp.append((name, "1", "Menu", module, screen, code))
			tmp += self.list[idx:]
			self.list = tmp
		else:
			self.list = []
			self.list.append((name, "1", "Menu", module, screen, code))
		return self.list

	def mkContent(self, n):
		if n <> None:
			xml = "\t\t<content>\n"
			xml += "\t\t\t<name>" + stringToXML(n[0]) + "</name>\n"
			if n[1] <> "":
				xml += "\t\t\t<sel>1</sel>\n"
			if n[3] <> "":
				xml += "\t\t\t<module>" + n[3] + "</module>\n"
			if n[4] <> "":
				xml += "\t\t\t<screen><![CDATA[" + n[4] + "]]></screen>\n"
			if n[5] <> "":
				xml += "\t\t\t<code><![CDATA[" + n[5] + "]]></code>\n"
			xml += "\t\t</content>\n"
		return xml

	def saveMenu(self,path):
		xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
		if self.list <> None:
			category = "Menu"
			xml += "<xml>\n\t<" + category + ">\n"
			for n in self.list:
				if n[0] <> "--":
					if category == n[2]:
						xml += self.mkContent(n)
					else:
						xml += "\t" + "</" + category + ">\n"
						category = n[2]
						xml += "\t" + "<" + category + ">\n"
						xml += self.mkContent(n)
			xml += "\t</" + category + ">\n</xml>\n"
		f = open(path, "w")
		f.write(xml)
		f.close()
