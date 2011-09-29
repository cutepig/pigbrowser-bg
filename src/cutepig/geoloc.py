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

import GeoIP
from cutepig import *
import cutepig.log as log
import cutepig.continents

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

class geolocator(object):
	def __init__(self, geoip_path):
		try :
			self.geo = GeoIP.open( geoip_path, GeoIP.GEOIP_MEMORY_CACHE)
		except:
			self.geo = None
	
	def __call__(self, addr ):
		if( not self.geo ) :
			return ( 'ZZ', 'ZZ' )
		
		loc = self.geo.country_code_by_addr ( ip_int_str (addr) )
		if ( loc not in cutepig.continents.countries ) :
			# theres the occasional bug where we get the continent for
			# the country so should we check that out in here?
			log.log( "geolocator: %s not found in continents" % loc )
			loc = 'ZZ'
			cont = 'ZZ'
		else :
			cont = cutepig.continents.countries[loc]
			
		return ( loc, cont )
		
###################
#
# Main
