#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
import os

from datasource import genericdatasource
from satxml import satxml
from lamedb import lamedb
from input import *


maindata = genericdatasource()

sources = [satxml, lamedb]

datasources = [maindata]

for source in sources:
	datasources.append(source())

for source in datasources:
	source.setDatasources(datasources)

while True:
	os.system("/usr/bin/clear")
	_list = []
	for index in list(range(len(datasources))):
		_list.append(datasources[index].getName() + (" (%d sats)" % len(list(datasources[index].transponderlist.keys()))))
	index = inputChoices(_list, "q", "quit")
	if index is None:
		break

	while True:
		print(datasources[index].getStatus())
		_list = []
		for action in datasources[index].getCapabilities():
			_list.append(action[0])
		action = inputChoices(_list)
		if action is None:
			break

		datasources[index].getCapabilities()[action][1]()
		#except:
		#	print sys.exc_info()
		#	print "sorry, could not execute that command"
