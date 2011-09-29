#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 30.8.2011

@author: hc
'''

###################
#
# Imports

import sys, datetime

###################
#
# Constants

###################
#
# Globals

_log_outfile = None
_log_opened = False
_error_outfile = None
_error_opened = False

def log(msg):
	global _log_outfile
	if(_log_outfile):
		# TODO: add date
		_log_outfile.write( "[%s] %s\n" % (datetime.datetime.now().strftime("%x %X"), msg) )
		
def error(msg):
	global _error_outfile
	if(_error_outfile):
		# TODO: add date
		_error_outfile.write( "[%s] %s\n" % (datetime.datetime.now().strftime("%x %X"), msg) )
	
# given file can be named "stdout" or "stderr", or it can be a
# file object or any object that has "write" function
# or it can be a filename
def init(log_outfile, error_outfile, log_append=True, error_append=True):
	global _log_outfile
	global _log_opened
	global _error_outfile
	global _error_opened
	
	close();
	_std = { "stdout" : sys.stdout, "stderr" : sys.stderr }
	if(log_outfile in _std):
		_log_outfile = _std[log_outfile]
	elif(getattr(_log_outfile, "write")):
		_log_outfile = log_outfile
	else:
		try :
			_log_outfile = open(log_outfile, "a" if log_append else "w")
			_log_opened = True
		except: _log_outfile = None 
		
	if(error_outfile in _std):
		_error_outfile = _std[error_outfile]
	elif(getattr(_error_outfile, "write")):
		_error_outfile = error_outfile
	else:
		try :
			_error_outfile = open(error_outfile, "a" if error_append else "w")
			_error_opened = True
		except: _error_outfile = None 
		
def close():
	global _log_outfile
	global _log_opened
	global _error_outfile
	global _error_opened
	
	if(_log_opened and _log_outfile):
		_log_outfile.close()
	if(_error_opened and _error_outfile):
		_error_outfile.close()
	
	_log_outfile = None
	_log_opened = False
	_error_outfile = None
	_error_opened = False

###################
#
# Helpers

###################
#
# Classes

###################
#
# Main
