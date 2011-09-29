#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-

# (c) 2011 Christian Holmberg
# This file is part of Pig browser.

# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

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
