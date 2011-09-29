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

import config, time, re
from datetime import datetime
from collections import deque, namedtuple

from cutepig import *
import cutepig.log as log
import cutepig.task
import cutepig.geoloc

from pigbrowser import *
import pigbrowser.tasks as tasks
import pigbrowser.protocol as protocol
import pigbrowser.dbmodels
from pigbrowser.duelstate import *

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

class Application:
	_instance = None
	PORT_RANGE_MIN = 6000
	PORT_RANGE_MAX = 6200
	# if its this long after last seen on master, free to remove
	LAST_MASTER_INTERVAL = config.master_update_interval * 2
	
	class ServerInfoState:
		def __init__(self,ip,updated,last_master):
			self._ip = ip
			self._lastUpdated = updated
			self._lastMaster = last_master
			
		def getIP(self):
			return self._ip
		def getLastMaster(self):
			return self._lastMaster
		def setLastMaster(self,t):
			self._lastMaster = t
		def getUpdated(self):
			return self._lastUpdated
		def setUpdated(self,t):
			self._lastUpdated = t

	def __init__(self):
		
		log.init(config.log_log_filename, config.log_error_filename,
					config.log_log_append, config.log_error_append)
		
		self._database = cutepig.database.Database(
				db=config.db_name, user=config.db_user,
				passwd=config.db_passwd,host=config.db_host)
		self._database.createTables(pigbrowser.dbmodels, None, None, True)
		
		self._geoloc = cutepig.geoloc.geolocator(config.geoip_path)
		self._taskManager = cutepig.task.TaskManager()
		self._activeServers = []	# active duel tasks
		self._serverInfos = deque()		# serverinfo states
		self._serverIPs = []		# list of current server ip's to run (ALL!)
		self._masterfetchers = []	# list of masterfetcher tasks
		
		# singleton tasks
		self._maintainer = tasks.Maintainer(self)
		self._pusher = tasks.ServerInfoPusher(self)
		# self._localfetcher = tasks.LocalServerListFetcher(self)
		self._cleaner = tasks.Cleaner(self)
		
		self._protocol = protocol.WarsowProtocol()
		self._portcount = self.PORT_RANGE_MIN
		
		# initiate master servers
		for master in config.masters :
			ip = cutepig.net.resolveHostname(master)
			masterfetcher = tasks.MasterListFetcher(self, ip)
			self._masterfetchers.append( masterfetcher )
			self._taskManager.addJob(time.time(), cutepig.task.PRIORITY_LOW, masterfetcher, ())
			
		self._taskManager.addJob(time.time()+1, cutepig.task.PRIORITY_LOW, self._maintainer, ())
		self._taskManager.addJob(time.time()+3.0, cutepig.task.PRIORITY_MEDIUM, self._pusher, ())
		# self._taskManager.addJob(time.time(), cutepig.task.PRIORITY_LOW, self._localfetcher, ())
		self._taskManager.addJob(time.time()+10.0, cutepig.task.PRIORITY_LOW, self._cleaner, ())
		
	def run(self):
		self._taskManager.runJobs()
		
	def getTaskManager(self):
		return self._taskManager
	
	def getProtocol(self):
		return self._protocol

	def getGeoloc(self):
		return self._geoloc
		
	def getDatabase(self):
		return self._database
	
	def getPort(self):
		self._portcount += 1
		if( self._portcount > self.PORT_RANGE_MAX ) :
			self._portcount = self.PORT_RANGE_MIN
		return self._portcount
	
	def bindSocket(self,soc):
		firstport = self.getPort()
		port = firstport
		while( True ) :
			try :
				soc.bind(('', port))
				break
			except:
				port = self.getPort()
			if( port == firstport ) :
				return False
		# log.log("bindSocket bound to port %d" % port)
		return True
	
	# signal that the master has stopped
	def masterStopped(self):
		# log.log("masterStopped (%d/%d servers)" % (len(self._serverInfos), len(self._activeServers)))
		#if( not self._pusher.isActive() ) :
		#	self._pusher.forceUpdate()
		pass
	
	# signal that duelinfo task has stopped
	def duelStopped(self, duel):
		if(duel in self._activeServers):
			self._activeServers.remove(duel)
		else:
			log.log("Application::duelStopped: job not in the list")
	
	# checks if server is on the works (called after master update)
	def addServer(self, ip):
		if(ip in self._serverIPs):
			# mark 'last-seen-on-master'
			for _serverinfo in self._serverInfos:
				if(_serverinfo.getIP() == ip):
					_serverinfo.setLastMaster(time.time())
			return
		
		_serverinfo = self.ServerInfoState(ip,0.0,time.time())
		# push to front (new server)
		self._serverInfos.append(_serverinfo)
		self._serverIPs.append(ip)
		
	def removeServer(self, _serverinfo):
		if(_serverinfo.getIP() in self._serverIPs):
			self._serverIPs.remove(_serverinfo.getIP())
		if(_serverinfo in self._serverInfos):
			self._serverInfos.remove(_serverinfo)
		
		# TODO: remove references from the database, ServerInfo, ServerPlayer etc..
		_cursor = self._database.cursor()
		# get the id
		_query = 'SELECT id FROM %s WHERE address = %%s' % dbmodels.ServerInfo.tablename
		_cursor.execute( _query, (_serverinfo.getIP()))
		_result = _cursor.fetchone()
		if(_result) :
			_id = _result[0]
			# players
			_query = 'DELETE FROM %s WHERE server_id = %%s' % dbmodels.ServerPlayer.tablename
			_cursor.execute(_query, (_id))
			# and the server
			_query = 'DELETE FROM %s WHERE id = %%s' % dbmodels.ServerInfo.tablename
			_cursor.execute(_query, (_id))
			
		# TODO: what to do with the active server? signal it to be
		# stopped when able to or just force-remove it in here?

	# called from ServerInfoPusher to fetch newest serverinfo
	def peekServer(self):
		if(len(self._serverInfos)):
			return self._serverInfos[-1]
		return None
	
	# called from ServerInfoPusher to put the newest serverinfo as oldest
	def rotateServers(self):
		self._serverInfos.rotate(1)
	
	# is a server with given ip on the active list
	def isServerActive(self, ip):
		for server in self._activeServers:
			if( server.getIP() == ip ) :
				return True
		return False

	def hasServers(self):
		return len(self._serverInfos) > 0
	
	def hasServerinfo(self, ip):
		return ip in self._serverIPs

	def migrateServerlist(self, ips):
		# remove old servers from passiveServers
		removables = []
		t = time.time()
		for _serverinfo in self._serverInfos:
			if( (t - _serverinfo.getLastMaster()) > self.LAST_MASTER_INTERVAL and _serverinfo.getIP() not in ips ) :
				removables.append(_serverinfo)
				
		# log.log("migrateServerlist removing %d servers" % (len(removables)))
		for removable in removables:
			self.removeServer(removable)
				
		# insert new servers
		for ip in ips:
			self.addServer(ip)
			
		# umm.. delete all?
		if(not len(self._serverIPs)):
			return

		# database cleanup now that we have new valid list of ips
		_cursor = self._database.cursor()
		
		# all servers that arent on the list anymore
		# FIXME array len 1 bug
		if( len(self._serverIPs) > 1 ) :
			_query = 'DELETE FROM %s WHERE address NOT IN %%s' % pigbrowser.dbmodels.ServerInfo.tablename
			_values = (self._serverIPs,)
		else:
			_query = 'DELETE FROM %s WHERE address != %%s' % pigbrowser.dbmodels.ServerInfo.tablename
			_values = (self._serverIPs[0],)
		_cursor.execute(_query, _values)
		
		# all players that arent in the list anymore
		_query = 'DELETE FROM %s WHERE server_id NOT IN (SELECT id FROM serverinfos)' % pigbrowser.dbmodels.ServerPlayer.tablename
		_cursor.execute(_query)
		

	# info is an object from protocols
	# TODO: factor this into duelstate module or smth
	def checkActiveDuel(self,info):
		addr = info['addr']
		
		# check if it exists on our list
		for _active in self._activeServers:
			if(_active.getIP() == addr):
				# rather than returning.. we could update the duel in here
				# log.log("checkActiveDuel: already active job")
				_active.processInfo(info)
				return
		
		if(DuelState.checkActiveDuel(info)):
			# initiate a duelfetcher job!
			#if( not self.db.IncomingExists( addr ) ) :
			#	self.db.AddIncoming( addr )
			job = tasks.DuelInfoFetcher(self, addr)
			self._taskManager.addJob(time.time(), cutepig.task.PRIORITY_HIGH, job, ())
			self._activeServers.append(job)

###################
#
# Main
