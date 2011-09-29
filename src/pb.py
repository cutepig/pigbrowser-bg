#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 8.8.2011

@author: hc
'''

###################
#
# Imports

import traceback

import cutepig
import cutepig.log
import pigbrowser
import pigbrowser.app

import atexit
import signal

###################
#
# Constants

###################
#
# Globals

###################
#
# Helpers

@atexit.register
def report_exit():
	cutepig.log.close()
	
def handle_term(signum, frame):
	if(signum == signal.SIGTERM):
		cutepig.log.log("Exiting by SIGTERM")
		exit(0)
	
###################
#
# Classes

###################
#
# Main
if __name__ == '__main__' :
	# let the app exit cleanly with exit(0) when killed externally
	signal.signal(signal.SIGTERM, handle_term)
	# python dont load env locales automatically
	cutepig.init_locale()
	# lets let the application initialize the logfile
	app = pigbrowser.app.Application()
	try :
		app.run()
	except KeyboardInterrupt:
		# no-op, just exit cleanly
		exit(0)
	except Exception as err:
		# report and dirty exit
		cutepig.log.error(traceback.format_exc())
		exit(1)
	# clean exit otherwise
	exit(0)
		