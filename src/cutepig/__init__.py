#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 7.8.2011

@author: hc
'''
###################
#
# Imports

import re
import datetime, operator
import os, locale

###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers

def safeint( a, b = 0 ):
	try: return int(a)
	except ValueError: return b

def is_ip(ip_str):
	pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
	if re.match(pattern, ip_str):
		return True
	else:
		return False

def total_seconds(_timedelta):
	if(getattr(_timedelta, 'total_seconds', None)) :
		return _timedelta.total_seconds()
	# python2.6 dont have total_seconds, this is the impl from docs
	return operator.truediv(_timedelta.microseconds +
						(_timedelta.seconds + _timedelta.days * 24 * 3600) * 10**6, 10**6)

# grabs the locale from the environment and sets its
def init_locale():
	lc_all = os.getenv("LC_ALL")
	if(lc_all):
		locale.setlocale(locale.LC_ALL, lc_all)

####################################
###
### 		IP_XXX_XXX
###
####################################

def ip_str_int ( ip ) :
	ss = ip.split ( '.' )
	if ( len(ss) != 4 ) :
		raise Exception ( "ip_str_int: ip not in 4 parts %s" % ip )
		
	return ((int(ss[0])*256+int(ss[1]))*256+int(ss[2]))*256+int(ss[3])
	
def ip_str_int_full ( ip ) :
	ips = ip.split ( ':' )
	if ( len(ips) == 1 ) :
		return ip_str_int ( ips[0] )
	elif ( len(ips) != 2 ) :
		raise Exception ( "ip_str_int_full: ip in what format?" )
		
	i = ip_str_int ( ips[0] )
	p = safeint ( ips[1] )
	
	return i + ( p<<32 )
	
	
def ip_int_str ( i ) :
	# and port is (i>>32) & 0xffff
	return "%d.%d.%d.%d" % ( ((i>>24)&0xff), (i>>16)&0xff, (i>>8)&0xff, (i&0xff) )
	
def ip_int_str_full ( i ) :
	return "%d.%d.%d.%d:%d" % ( ((i>>24)&0xff), (i>>16)&0xff, (i>>8)&0xff, (i&0xff), (i>>32)&0xffff )
	
	
def ip_int_tuple ( i ) :
	return ( i&0xffffffff, (i>>32)&0xffff )
	
def ip_int_tuple_s ( i ) :
	ip, port = ip_int_tuple ( i )
	return ( ip_int_str (ip), port )
	
def ip_tuple_int ( i ) :
	return ( i[0] + (i[1]<<32) )

def ip_tuple_int_s ( i ) :
	i0 = ip_str_int ( i[0] )
	return ( i0 + (i[1]<<32) )

#####
##### LIST UNIQIFICATION thanks to http://www.peterbe.com/plog/uniqifiers-benchmark
#####

def _uniqify(seq, idfun=None):
	seen = set()
	if idfun is None:
		for x in seq:
			if x in seen:
				continue
			seen.add(x)
			yield x
	else:
		for x in seq:
			x = idfun(x)
			if x in seen:
				continue
			seen.add(x)
			yield x
			
			
def uniqify(seq, idfun=None): # f10 but simpler
	# Order preserving
	return list(_uniqify(seq, idfun))

###################
#
# Classes
