#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 8.8.2011

@author: hc
'''

###################
#
# Imports


###################
#
# Constants

###################
#
# Globals

# ch : pigbrowser is working on homedir here, thats
# why we are defining it here.
homepath = ''
geoip_path = '%s/code/GeoIP.dat' % homepath

# logfile (leave as None to disable logging
log_log_filename = 'stdout'
log_log_append = True
log_error_filename = 'stderr'
log_error_append = True

# database
db_host = ''
db_user = ''
db_passwd= ''
db_name = ''
# db_name = 'pb-test'

# game
masters = [
	'dpmaster.deathmask.net:27950',
	#'excalibur.nvg.ntnu.no:27950',	# excalibur cant handle the gametype=duel stuff
	#'ghdigital.com:27950',		# this has been timeouting for awhile
	
	# 'eu.master.warsow.net:27950',	# does this even work?
]

# interval to fetch master serverlist
master_update_interval = 20.0	# 30.0 in seconds
# interval when fetching protocol queries
query_update_interval = 0.05	# in seconds
query_socket_timeout = 3.0
# interval between serverinfos for one server
serverinfo_update_interval = 30.0 # 60.0
# time serverinfopusher sleeps when not active
serverinfo_sleep_interval = 5.0
# time serverinfopusher sleeps when it is active
serverinfo_active_interval = 0.2
# number of concurrent serverinfos to fetch
serverinfo_concurrent_jobs = 10

###################
#
# Helpers

###################
#
# Classes

###################
#
# Main
