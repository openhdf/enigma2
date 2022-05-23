# usage: genmetaindex.py <xml-files>  > index.xml
from __future__ import absolute_import
from sys import version_info, argv, stdout
from os import path as os_path
from xml.etree.ElementTree import ElementTree, Element

root = Element("index")
encoding = ("unicode" if version_info[0] >= 3 else "utf-8")

for _file in argv[1:]:
	p = ElementTree()
	p.parse(_file)

	package = Element("package")
	package.set("details", os_path.basename(_file))

	# we need all prerequisites
	package.append(p.find("prerequisites"))

	info = None
	# we need some of the info, but not all
	for i in p.findall("info"):
		if not info:
			info = i
	assert info

	for i in info[:]:
		if i.tag not in ["name", "packagename", "packagetype", "shortdescription"]:
			info.remove(i)

	for i in info[:]:
		package.set(i.tag, i.text)

	root.append(package)


def indent(elem, level=0):
	i = "\n" + level * "\t"
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "\t"
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


indent(root)

ElementTree(root).write(stdout, encoding=encoding)
