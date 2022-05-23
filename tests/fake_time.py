from __future__ import absolute_import
from time import time, sleep

real_time = None
time_offset = 0


def setRealtime():
	global real_time
	real_time = time


def setIdealtime():
	global real_time
	real_time = lambda: 0


def setTime(now):
	global time_offset
	time_offset = real_time() - now


setIdealtime()
setTime(0)


def my_time():
	return real_time() - time_offset


time = my_time


def my_sleep(sleep):
	global time_offset
	time_offset -= sleep
	print("(faking %f seconds)" % sleep)


sleep = my_sleep
