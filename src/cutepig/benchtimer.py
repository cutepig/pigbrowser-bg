#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 22.5.2011

@author: hc
'''

###################
#
# Imports

import datetime
import cutepig.log as log

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

class benchtimer( object ):
	def __init__(self, s):
		self.startTime = datetime.datetime.now()
		log.log( "%s - %s" % ( self.startTime, s ) )
		
	def __call__(self, s):
		endTime = datetime.datetime.now()
		log.log( "%s ( time %s )" % ( s, (endTime - self.startTime)))
		
###################
#
# Main
