from __future__ import absolute_import

from re import compile as re_compile


def elementsWithTag(el, tag):
	"""filters all elements of childNode with the specified function
	example: nodes = elementsWithTag(childNodes, lambda x: x == "bla")"""

	from xml.dom.minidom import Element

	# fiiixme! (works but isn't nice)
	if isinstance(tag, str):
		s = tag
		tag = lambda x: x == s

	for x in el:
		if x.nodeType != Element.nodeType:
			continue
		if tag(x.tagName):
			yield x


def mergeText(nodelist):
	rc = ""
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc = rc + node.data
	return rc


def stringToXML(text):
	illegal_xml_chars_RE = re_compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')
	text = illegal_xml_chars_RE.sub('', text)
	return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;')
