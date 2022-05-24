#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from os import listdir
from os import path as os_path
from re import compile
from sys import argv
from xml.sax import make_parser
from xml.sax.handler import ContentHandler, property_lexical_handler

from six import ensure_str

try:
	from _xmlplus.sax.saxlib import LexicalHandler
	no_comments = False
except ImportError:
	class LexicalHandler:
		def __init__(self):
			pass
	no_comments = True


class parseXML(ContentHandler, LexicalHandler):
	def __init__(self, attrlist):
		self.isPointsElement, self.isReboundsElement = 0, 0
		self.attrlist = attrlist
		self.last_comment = None
		self.ishex = compile('#[0-9a-fA-F]+\Z')

	def comment(self, comment):
		if "TRANSLATORS:" in comment:
			self.last_comment = comment

	def startElement(self, name, attrs):
		for x in ["text", "title", "value", "caption", "description"]:
			try:
				k = ensure_str(attrs[x])
				if k.strip() != "" and not self.ishex.match(k):
					attrlist.add((k, self.last_comment))
					self.last_comment = None
			except KeyError:
				pass


parser = make_parser()

attrlist = set()

contentHandler = parseXML(attrlist)
parser.setContentHandler(contentHandler)
if not no_comments:
	parser.setProperty(property_lexical_handler, contentHandler)

for arg in argv[1:]:
	if os_path.isdir(arg):
		for _file in listdir(arg):
			if _file.endswith(".xml"):
				parser.parse(os_path.join(arg, _file))
	else:
		parser.parse(arg)

	attrlist = list(attrlist)
	attrlist.sort(key=lambda a: a[0])

	for (k, c) in attrlist:
		print()
		print('#: ' + arg)
		k.replace("\\n", "\"\n\"")
		if c:
			for l in c.split('\n'):
				print("#. ", l)
		print('msgid "' + ensure_str(k) + '"')
		print('msgstr ""')

	attrlist = set()
