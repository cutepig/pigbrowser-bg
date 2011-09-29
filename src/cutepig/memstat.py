#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 23.5.2011

@author: hc
'''

###################
#
# Imports

import os
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

class memstat(object):
	
	def __init__(self):
		# get the pid of our process
		self.pid = os.getpid()
		
		# get the pagesize of our process
		pipe = os.popen( 'getconf PAGESIZE' )
		pagesize = pipe.read()
		pipe.close()
		
		self.pageSize = int( pagesize )

	def prettyprint(self, bytes):
		if( bytes > 1024 ) :
			if( bytes > 1048576 ) :
				return "%.2fMb" % ( float(bytes) / 1048576.0 )
			return "%.2fKb" % ( float(bytes) / 1024.0 )
		
		return "%d bytes" % bytes
	
	def __call__(self, msg):
		# get the current mem usage
		fp = open( '/proc/%d/statm' % self.pid, 'r' )
		statm = fp.read()
		fp.close()
		
		# all of this in pages
		# progSize, rssSize, sharedSize, codeSize, libSize, stackSize, dirtySize
		stats = statm.split()
		rssSize = int( stats[1] ) * self.pageSize
		
		log.log( '%s ( mem usage: %s )' % ( msg, self.prettyprint(rssSize)))
		
###################
#
# Main
