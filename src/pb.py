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
		
