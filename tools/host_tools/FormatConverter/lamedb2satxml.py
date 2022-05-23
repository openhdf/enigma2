#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
from datasource import genericdatasource
from satxml import satxml
from lamedb import lamedb

from sys import argv, exit as sys_exit

if len(argv) != 3:
	print("usage: %s <lamedb> <satellites.xml>" % argv[0])
	sys_exit()

gen = genericdatasource()
db = lamedb(argv[1])
xml = satxml(argv[2])

db.read()
gen.source = db
gen.destination = xml
gen.docopymerge(action="copy")
xml.write()
