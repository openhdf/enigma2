#!/usr/bin/python

from sys import argv
from sys import exit as sys_exit

from datasource import genericdatasource
from lamedb import lamedb
from satxml import satxml

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
