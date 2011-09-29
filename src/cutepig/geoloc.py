#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 22.5.2011

@author: hc
'''

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
