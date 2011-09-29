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
