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
