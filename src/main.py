#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 7.8.2011

@author: hc
'''

###################
#
# Imports

import time

from cutepig import task
from cutepig import *

###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers

###################
#
# Classes

class MyTask( task.Task ) :
	messages = [ "hahaha", "ehheeh", "hohohoho", "Merry Christmas!", "Hello World!", "foobar" ]
	
	def __init__(self, count,msg):
		task.Task.__init__(self)
		self._count = count
		self._orgcount = count
		self._msg = msg
		
	def run(self, *args):
		if( self._count <= 0 ) :
			print( "Removing myself %s" % self._msg )
			self.removeSelf()
			# add a new task for test
			if( self._orgcount > 0 ) :
				print( "Adding a new task with msg %s" % self.messages[self._orgcount-1])
				self._taskmanager.addJob( time.time() + 0.3, 1, MyTask(self._orgcount-1, self.messages[self._orgcount-1]), () )
			return
			
		print( "MyTask executed %s" % self._msg )
		
		# put to queue
		self.setNextUpdate( time.time() + 0.3 )
		
		self._count -= 1
		
###################
#
# Main

if __name__ == '__main__' :
	tm = task.TaskManager()
	tm.addJob( time.time(), 1, MyTask( 5, "first message" ) )
	tm.runJobs()