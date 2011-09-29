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

"""
different tasks for pigbrowser:
	- fetch master-server list
	- push tasks to fetch serverinfo's and duelinfo's
	- fetch simple server info
	- fetch specific info for ongoing duel (and check stuff)
	- store duel-result to database (separate to not stall other important jobs?)
	
	- maintain task dependancy or ordering
"""

###################
#
# Imports

import datetime, select

import cutepig.net
import cutepig.task
import cutepig.log as log
from cutepig import *

import pigbrowser.protocol
import pigbrowser.dbmodels as models
from pigbrowser import *
from pigbrowser.duelstate import *

import config

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

# simple serverinfo
class ServerInfoFetcher( cutepig.task.Task ):
	QUERY_UPDATE_INTERVAL = config.query_update_interval
	def __init__(self, pusher, ip):
		cutepig.task.Task.__init__(self)
		
		self._ip = ip
		self._pusher = pusher
		self._app = pusher.getApp()
		self._socket = None
		self._query = None

		self.setPriority( cutepig.task.PRIORITY_LOW )
		self._newQuery()
		
	def _newQuery(self):
		# TODO: use sockets from pool or something
		self._socket = cutepig.net.Socket(config.query_socket_timeout, False)
		self._query = protocol.ServerQuery( self._socket, self._ip, self._app.getProtocol() )
		self._query.startServerQuery(True)
		
	def _inDatabase(self, _cursor):
		_query = 'SELECT id FROM %s WHERE address = %%s' % models.ServerInfo.tablename
		_values = ( self._ip )
		_cursor.execute( _query, _values )
		_result = _cursor.fetchone()
		if( _result ) :
			return _result[0]
		return 0

	def _emitServerInfo(self, info):
		_addr = info['addr']
		_geoloc = self._app.getGeoloc()
		_players = []
		if( 'error' not in info and 'timeout' not in info ) :
			_serverinfo = models.ServerInfo(info)
			# read players
			if('players' in info) :
				_list = info['players']
				for _player in _list:
					_players.append(models.ServerPlayer(_player))
				_serverinfo.players = _players
		else :
			_serverinfo = models.ServerInfo()
			_serverinfo.name = '(Server timeouted)' if 'timeout' in info else '(Server error)'
			_serverinfo.sortname = ''
			_serverinfo.flags = FLAG_TIMEOUT
			
		# write to database
		_db = self._app.getDatabase()
		_cursor = _db.cursor()
		
		_id = self._inDatabase(_cursor)
		
		# first remove all players that are supposed to be on this server
		# (optimize this in the future and use UPDATE for existing players) 
		_query = 'delete from %s where server_id=%%s' % models.ServerPlayer.tablename
		_values = (_id)
		_cursor.execute(_query, _values)
		
		# now lets see weather we update or insert the serverinfo
		if(not _id) :
			# apply these only for new serverinfo's 
			_serverinfo.address = _addr
			_serverinfo.address2 = ip_int_str_full(_addr)
			_serverinfo.location, _serverinfo.continent = _geoloc(_addr)
			
			_query = '''insert into %s
				(address, address2, name, sortname, location, continent, mapname, numplayers,
				numspecs, maxclients, gamename, flags, timestamp, updateround, skilllevel)
				values( %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s,
				%%s, %%s, %%s, %%s, %%s, %%s, %%s) 
				''' % models.ServerInfo.tablename
			_values = (_serverinfo.address, _serverinfo.address2, _serverinfo.name, _serverinfo.sortname,
					_serverinfo.location, _serverinfo.continent, _serverinfo.mapname, _serverinfo.numplayers,
					_serverinfo.numspecs, _serverinfo.maxclients, _serverinfo.gamename, _serverinfo.flags,
					_serverinfo.timestamp, _serverinfo.updateround, _serverinfo.skilllevel)
			_cursor.execute(_query, _values)
			_id = _db.insert_id()
		else:
			_query = '''update %s set
	 			name=%%s, sortname=%%s, mapname=%%s, numplayers=%%s, numspecs=%%s, maxclients=%%s,
	 			gamename=%%s, flags=%%s, timestamp=%%s, updateround=%%s, skilllevel=%%s
	 			where id=%%s''' % models.ServerInfo.tablename
			_values = (_serverinfo.name, _serverinfo.sortname, _serverinfo.mapname, _serverinfo.numplayers,
					_serverinfo.numspecs, _serverinfo.maxclients, _serverinfo.gamename, _serverinfo.flags,
					_serverinfo.timestamp, _serverinfo.updateround, _serverinfo.skilllevel, _id)
			_cursor.execute(_query, _values)
		
		# write down the players
		for _player in _players:
			# TODO: batch-insert multiple with values(..) values(...)
			_player.server_id = _id
			_query = '''insert into %s
				(server_id, team, score, ping, name, updateround)
				values(%%s, %%s, %%s, %%s, %%s, %%s)
				''' % models.ServerPlayer.tablename
			_values = (_id, _player.team, _player.score,
					_player.ping, _player.name, _player.updateround)
			_cursor.execute(_query, _values)
		
		_db.commit()
		_serverinfo.id = _id
		return _serverinfo

	def getIP(self):
		return self._ip
	
	# TODO: figure out why ServerinfoFetcher::run sometimes takes more than 100ms
	def run(self, args):
		if( not self._query.checkServerQuery() ) :
			# no data, schedule a new update and wait for it
			self.setNextUpdate( self.time() + self.QUERY_UPDATE_INTERVAL )
			return
		
		# ok, get the info, nullify the query and socket
		info = self._query.finishServerQuery()
		self._query = None
		self._socket.close()
		self._socket = None
		
		self.removeSelf()
		self._pusher.serverinfoStopped(self)
		
		# emit the serverinfo to database
		_serverinfo = self._emitServerInfo(info)
		
		# here, check if we have valid duel going on, if so pass it back to app
		# which will initiate new duelinfofetcher process
		if(_serverinfo.numplayers == 2 and _serverinfo.flags != FLAG_TIMEOUT):
			self._app.checkActiveDuel(info)
		else :
			pass
			# log.log("not checking active duel (%s)" % ("numplayers" if _serverinfo.numplayers!=2 else "timeout"))
			
		return
	
		# comment out above return to print this
		if( 'timeout' in info ) :
			log.log("serverinfo finished %s (timeout)" % (ip_int_str_full(self._ip)))
		elif( 'error' in info ) :
			log.log("serverinfo finished %s (error)" % (ip_int_str_full(self._ip)))
		else :
			log.log("serverinfo finished %s" % (ip_int_str_full(self._ip)))

###################

# this pushes ServerInfoFetchers (singleton class)
class ServerInfoPusher( cutepig.task.SingletonTask ):
	_instance = None
	MAX_CONCURRENT_INFOS = config.serverinfo_concurrent_jobs
	ACTIVE_UPDATE_INTERVAL = config.serverinfo_active_interval
	SLEEP_UPDATE_INTERVAL = config.serverinfo_sleep_interval
	MIN_SERVERINFO_INTERVAL = config.serverinfo_update_interval
	
	def __init__(self, app):
		cutepig.task.SingletonTask.__init__(self)
		
		self._jobs = []
		self._app = app
		
		self.setPriority( cutepig.task.PRIORITY_LOW )

	def run(self, args):
		# check if we need to push more jobs in
		needjobs = self.MAX_CONCURRENT_INFOS - len(self._jobs)
		if( needjobs > 0 and self._app.hasServers() ) :
			#log.log("ServerInfoPusher: adding %d jobs" % needjobs)
			taskManager = self._app.getTaskManager()
			for i in xrange(needjobs):
				server = self._app.peekServer()
				if( not server or (self.time()-server.getUpdated()) < self.MIN_SERVERINFO_INTERVAL ) :
					break
				job = ServerInfoFetcher(self, server.getIP())
				taskManager.addJob( self.time(), cutepig.task.PRIORITY_LOW, job, () )
				self._jobs.append( job )
				server.setUpdated(self.time())
				self._app.rotateServers()
			
		# let the jobs run, schedule an update down the road
		if( len(self._jobs) ) :
			self.setNextUpdate( self.time() + self.ACTIVE_UPDATE_INTERVAL )
		else :
			self.setNextUpdate( self.time() + self.SLEEP_UPDATE_INTERVAL )

	def getApp(self):
		return self._app
	
	# signal that serverinfo has stopped
	def serverinfoStopped(self,serverinfo):
		if(serverinfo in self._jobs):
			self._jobs.remove(serverinfo)

###################

# fetch serverlist from master
class MasterListFetcher( cutepig.task.Task ):
	QUERY_UPDATE_INTERVAL = config.query_update_interval
	
	def __init__(self, app, ip):
		cutepig.task.Task.__init__(self)
	
		self._app = app
		self._ip = ip
		self._socket = None
		self._query = None
		self._active = False
	
		self.setPriority( cutepig.task.PRIORITY_LOW )	
		self._newQuery()
		
	def run(self, args):
		# what state? do we have to start a new query?
		if( not self._query ) :
			# initiate new query
			self._newQuery()
			self.setNextUpdate( self.time() + self.QUERY_UPDATE_INTERVAL )
			return
		
		# we are already running a query, see if we have data available
		if( not self._query.checkMasterQuery() ) :
			# no data, schedule a new update and wait for it
			self.setNextUpdate( self.time() + self.QUERY_UPDATE_INTERVAL )
			return
		
		# ok, get the info, nullify the query and socket
		# log.log("finishing the masterquery")
		ips = self._query.finishMasterQuery()
		self._query = None
		self._socket.close()
		self._socket = None
		self._active = False
		
		# add the IP's to our global list
		self._app.migrateServerlist( ips )
		
		# set next update in 1 mins
		self.setNextUpdate( self.time() + config.master_update_interval )
		self._app.masterStopped()

	def _newQuery(self):
		# TODO: use sockets from pool or something
		# log.log("MasterListFetcher::_newQuery: ip %s" % ip_int_str_full(self._ip))
		self._socket = cutepig.net.Socket(config.query_socket_timeout, False)
		self._query = protocol.ServerQuery( self._socket, self._ip, self._app.getProtocol() )
		self._query.startMasterQuery(True, 'duel')
		self._active = True

###################

class LocalServerListFetcher( cutepig.task.Task):	
	PORT_START = 44400
	PORT_COUNT = 10
	
	def __init__(self, app):
		cutepig.task.Task.__init__(self)
		
		self._app = app
		self._ips = [ ip_str_int_full("127.0.0.1:%d" % _port) for _port in xrange(self.PORT_START, self.PORT_START+self.PORT_COUNT) ]
		
	def run(self, args):
		# push all of the ip's to the global list
		self._app.migrateServerlist( self._ips )
		self.setNextUpdate( self.time() + config.master_update_interval )
		self._app.masterStopped()

###################

# fetch specific duel info and check stuff on it
class DuelInfoFetcher( cutepig.task.Task ):
	QUERY_UPDATE_INTERVAL = config.query_update_interval
	
	# ELO DEFAULTS
	RATING_DEFAULT = 1200.0
	RATING_BOTTOM = 400.0
	RATING_PRO = 2400.0	# rating where K = 10
	RATING_MINGAMES = 30	# num of games when below K=25, and above K=15

	def __init__(self, app, ip):
		cutepig.task.Task.__init__(self)
	
		self._app = app
		self._ip = ip
		self._socket = None
		self._query = None
		self._currentState = None
		self._lastState = None
	
		self.setPriority( cutepig.task.PRIORITY_HIGH )
		self._newQuery()
		
	def _newQuery(self):
		# TODO: use sockets from pool or something
		# log.log("MasterListFetcher::_newQuery: ip %s" % ip_int_str_full(self._ip))
		self._socket = cutepig.net.Socket(config.query_socket_timeout, False)
		self._query = protocol.ServerQuery( self._socket, self._ip, self._app.getProtocol() )
		self._query.startServerQuery(True)
		
	# this doesnt check for endgame result or anything.. just
	# drop the task from all lists	
	def _dropSelf(self, msg=None):
		self._app.duelStopped(self)
		self.removeSelf()
		if(msg):
			log.log("[%s] DuelInfo dropped: %s" % (str(datetime.datetime.now()), msg))
		
	# objects are dbmodels.PlayerRating's
	@staticmethod
	def _calculateRating(player1, player2):
		_delta = player2.rating - player1.rating
		_ea = 1.0 / (1.0+(pow(10.0, _delta/400.0)))
		if(player1.numgames < DuelInfoFetcher.RATING_MINGAMES):
			_K = 25.0
		elif(player1.rating < DuelInfoFetcher.RATING_PRO):
			_K = 15.0
		else:
			_K = 10.0
			
		_p1 = player1._player
		_p2 = player2._player
		if(_p1._score > _p2._score):
			_win = 1.0
		elif(_p1._score < _p2._score):
			_win = 0.0
		else:
			_win = 0.5
		
		player1.rating += _K * (_win - _ea)
		player2.rating += _K * ((1.0 - _win) - _ea)
		player1.rating = max(player1.rating, DuelInfoFetcher.RATING_BOTTOM)
		player2.rating = max(player2.rating, DuelInfoFetcher.RATING_BOTTOM)
		
	# get the other player than pl from the list
	@staticmethod
	def _otherPlayer(pl, players):
		if(pl == players[0]):
			return players[1]
		return players[0]
	
	def _emitAnyState(self, state, reliable):
		_cursor = self._app.getDatabase().cursor()
		# we first need to resolve the PlayerRatings
		_players = []
		for _pl in state._players:
			_other = self._otherPlayer(_pl, state._players)
			# check if this is in the database
			_query = 'SELECT * FROM %s WHERE name=%%s' % dbmodels.PlayerRating.tablename
			_values = (_pl._name,)
			_cursor.execute( _query, _values )
			_r = _cursor.fetchone()
			if(_r) :
				# id, name, numgames, wins, losses, ties, kills, deaths, lastgame, rating
				_prating = dbmodels.PlayerRating(_r)
			else:
				# create new player
				_prating= dbmodels.PlayerRating()
				_prating.name = _pl._name
				_prating.rating = DuelInfoFetcher.RATING_DEFAULT
				
			_prating.numgames += 1
			_prating.wins += 1 if(_pl._score > _other._score) else 0
			_prating.losses += 1 if(_other._score > _pl._score) else 0
			_prating.ties += 1 if(_other._score == _pl._score) else 0
			_prating.kills += _pl._score
			_prating.deaths += _other._score
			_prating.lastgame = datetime.datetime.utcnow()
			
			# insert-hack
			_prating._player = _pl
			_prating._oldrating = _prating.rating
			_players.append(_prating)
		
		# calculate ratings now that we have info on both players
		if(reliable):
			self._calculateRating(_players[0], _players[1])
		
		for _prating in _players:
			if(_prating.id):
				_query = '''update %s
					set numgames=%%s, wins=%%s, losses=%%s, ties=%%s,
					kills=%%s, deaths=%%s, lastgame=%%s, rating=%%s
					where id=%%s''' % dbmodels.PlayerRating.tablename
				_values = (_prating.numgames, _prating.wins, _prating.losses, _prating.ties,
						_prating.kills, _prating.deaths, _prating.lastgame,
						round(_prating.rating, 2), _prating.id)
				_cursor.execute(_query, _values)
			else:
				_query = '''insert into %s
					(name, numgames, wins, losses, ties, kills, deaths, lastgame, rating)
					values( %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)''' % dbmodels.PlayerRating.tablename
				_values = (_prating.name, _prating.numgames, _prating.wins, _prating.losses,
						_prating.ties, _prating.kills, _prating.deaths, _prating.lastgame,
						round(_prating.rating, 2))
				_cursor.execute(_query, _values)
				_prating.id = self._app.getDatabase().insert_id(_cursor)
				
		# now insert the matchresult
		_mresult = dbmodels.MatchResult()
		_mresult.matchtime = datetime.datetime.utcnow()
		_mresult.overtime = state._overtime
		_mresult.reliable = reliable
		_mresult.address = self._ip
		_mresult.location,cont = self._app.getGeoloc()(self._ip)
		_mresult.mapname = state._mapname
		
		_query = '''insert into %s
			(matchtime, overtime, reliable, address, location, mapname)
			values(%%s, %%s, %%s, %%s, %%s, %%s)
			''' % dbmodels.MatchResult.tablename
		_values = (_mresult.matchtime, _mresult.overtime, _mresult.reliable,
				_mresult.address, _mresult.location, _mresult.mapname)
		_cursor.execute(_query, _values)
		_mresult.id = self._app.getDatabase().insert_id(_cursor)
		
		# and then the matchplayers
		for _prating in _players:
			_pl = _prating._player
			_prating._delta = _prating.rating - _prating._oldrating
			_query = '''insert into %s
				(rating_id, result_id, name, score, rating, delta)
				values(%%s, %%s, %%s, %%s, %%s, %%s)
				''' % dbmodels.MatchPlayer.tablename
			_values = (_prating.id, _mresult.id, _pl._name, _pl._score,
					round(_prating._oldrating, 2), round(_prating._delta, 2 ))
			_cursor.execute(_query, _values)
			
		# DONE!
		self._app.getDatabase().commit()
		_cursor.close()
		
	def _emitCurrentState(self):
		_players = self._currentState._players
		_reliable = self._currentState.isReliable()
		_ragequit = self._currentState.checkRagequit(self._lastState)
		if(_ragequit):
			# _players.append(_ragequit)
			_reliable = False
			log.log("** RAGEQUIT: %s" % (_ragequit._name))
		if(not _reliable):
			zero_zero_bug = False
			if(len(_players)==2 and _players[0]._score == 0 and _players[1]._score == 0 ):
				zero_zero_bug = True
			self._emitLastState(zero_zero_bug)
			return
		
		if(len(_players) != 2):
			log.log("[%s] DuelInfo::_emitCurrentState: len(_players) != 2 (%s)?" % (str(datetime.datetime.now()), _players))
			return
		
		# fix the overtime flag from laststate
		if(self._lastState):
			self._currentState._overtime = self._lastState._overtime
		
		# DEBUG	
		log.log("[%s] DuelInfo: FINAL SCORE %s - %s: %d - %d (%s)" %
			(str(datetime.datetime.now()),  _players[0]._name, _players[1]._name, _players[0]._score,
			_players[1]._score, "reliable" if(_reliable) else "non reliable"))
		
		self._emitAnyState(self._currentState, _reliable)
	
	def _emitLastState(self, zero_zero_bug=False):
		_players = self._lastState._players
		_reliable = False
		# no ragequit in here
		if(len(_players) != 2):
			log.log("[%s] DuelInfo::_emitLastState: len(_players) != 2 (%s)?" % (str(datetime.datetime.now()), _players))
			return
		
		if(zero_zero_bug):
			_currtime = self._lastState._currtime
			_timelimit = self._lastState._timelimit
			# if we were very close to the end use the scoreline as reliable
			if(_currtime and _timelimit and cutepig.total_seconds(_timelimit - _currtime) < 5):
				_reliable = True
		# DEBUG
		_matchtime = self._lastState._matchtime if self._lastState._matchtime!=None else "unknown"
		log.log("[%s] DuelInfo: LAST SCORE %s - %s: %d - %d (%s)(%s)" %
			(str(datetime.datetime.now()), _players[0]._name, _players[1]._name, _players[0]._score, _players[1]._score,
			"reliable" if(_reliable) else "non reliable", _matchtime))
		
		self._emitAnyState(self._lastState, _reliable)
		
	# setups next update too or drops itself if done
	def processInfo(self, info):
		# SWAP NEW/OLD STATE
		self._lastState = self._currentState
		if(not self._currentState):
			self._currentState = DuelState(self, info)
			if(len(self._currentState._players) == 2):
				log.log("[%s] Starting to follow %s - %s" % (str(datetime.datetime.now()), self._currentState._players[0]._name, self._currentState._players[1]._name))
		else:
			self._currentState = DuelState(self, info)
		
		# DO STUFF.. LOGIC..
		if(not self._currentState.isValid()):
			# num timeouts/errors?
			# do what? use lastState?
			self._dropSelf("NOT VALID")
			return
		
		if(self._currentState.checkFinished(self._lastState)):
			self._emitCurrentState()
			self._dropSelf("FINISHED")
			return
		
		if(self._currentState.checkNewGame(self._lastState)):
			self._emitLastState()
			self._dropSelf("NEW GAME")
			return
		
		# DEBUG inform score here
		_players = self._currentState._players
		# log.log("[%s] Intermediate score %s - %s: %d - %d @ %s" % (str(datetime.datetime.now()),
		#	_players[0]._name, _players[1]._name, _players[0]._score,_players[1]._score, self._currentState._matchtime))

		# schedule next update, minimum interval 1 second, max 30
		delta = self._currentState.getRemainingSeconds() * 0.8
		delta = min( 30.0, max( 1.0, delta ) )
		self.setNextUpdate( self.time() + delta )
		
	def run(self, args):
		# what state? do we have to start a new query?
		if( not self._query ) :
			# initiate new query
			self._newQuery()
			self.setNextUpdate( self.time() + self.QUERY_UPDATE_INTERVAL )
			return
		
		# we are already running a query, see if we have data available
		if( not self._query.checkServerQuery() ) :
			# no data, schedule a new update and wait for it
			self.setNextUpdate( self.time() + self.QUERY_UPDATE_INTERVAL )
			return
		
		# ok, get the info, nullify the query and socket
		info = self._query.finishServerQuery()
		self._query = None
		self._socket.close()
		self._socket = None
		
		self.processInfo(info)
		
	def getIP(self):
		return self._ip

###################

# this cleans up old ratings and matches
class Cleaner( cutepig.task.SingletonTask ):
	_instance = None
	UPDATE_INTERVAL = 3600.0
	OLD_MATCHES_DAYS = 28
	OLD_RATINGS_DAYS = 28
	def __init__(self, app):
		cutepig.task.SingletonTask.__init__(self)
		self._app = app
		
	def run(self, args):
		_db = self._app.getDatabase()
		_cursor = _db.cursor()
		
		# this cleans all old matches and their associated players
		# select old match id's
		_query = """
			SELECT id FROM %s
			WHERE matchtime < SUBDATE(NOW(), INTERVAL %s DAY)
			""" % (models.MatchResult.tablename, self.OLD_MATCHES_DAYS)
		_cursor.execute(_query) 
		_r = _cursor.fetchall()
		if(len(_r)):
			_result_ids = [_rr[0] for _rr in _r]
			# delete associated players
			if(len(_result_ids)==1):
				_result_ids = _result_ids[0]
				_query_players = "DELETE FROM %s WHERE result_id=%%s" % models.MatchPlayer.tablename
				_query_results = "DELETE FROM %s WHERE id=%%s" % models.MatchResult.tablename
			else:
				_query_players = "DELETE FROM %s WHERE result_id in %%s" % models.MatchPlayer.tablename
				_query_results = "DELETE FROM %s WHERE id in %%s" % models.MatchResult.tablename
			_cursor.execute(_query_players,(_result_ids,))
			_cursor.execute(_query_results,(_result_ids,))
			
		# this cleans up all associated matches and players and ratings
		# for the players that havent played in xxx days

		# select old ratings
		_query = """
			SELECT id FROM %s
			WHERE lastgame < SUBDATE(NOW(), INTERVAL %s DAY)
			""" % (models.PlayerRating.tablename, self.OLD_RATINGS_DAYS)
		_cursor.execute(_query) 
		_r = _cursor.fetchall()
		if(len(_r)):
			_ids = [_rr[0] for _rr in _r]
			# select associated matches and delete ratings
			if(len(_ids)==1):
				_ids = _ids[0]
				_query = "SELECT DISTINCT result_id FROM %s WHERE id=%%s" % models.MatchPlayer.tablename
				_query_ratings = "DELETE FROM %s WHERE id=%%s" % models.PlayerRating.tablename
			else:
				_query = "SELECT DISTINCT result_id FROM %s WHERE id IN %%s" % models.MatchPlayer.tablename
				_query_ratings = "DELETE FROM %s WHERE id IN %%s" % models.PlayerRating.tablename
			_cursor.execute(_query, (_ids,))
			_s = _cursor.fetchall()
			if(len(_s)):
				# delete players associated with matches along with the matches
				_result_ids = [_ss[0] for _ss in _s]
				if(len(_result_ids)==1):
					_result_ids = _result_ids[0]
					_query_players = "DELETE FROM %s WHERE result_id=%%s" % models.MatchPlayer.tablename
					_query_results = "DELETE FROM %s WHERE id=%%s" % models.MatchResult.tablename
				else:
					_query_players = "DELETE FROM %s WHERE result_id IN %%s" % models.MatchPlayer.tablename
					_query_results = "DELETE FROM %s WHERE id IN %%s" % models.MatchResult.tablename
				_cursor.execute(_query_players,(_result_ids,))
				_cursor.execute(_query_results,(_result_ids,))
			_cursor.execute(_query_ratings,(_ids,))

		# nicer version would zero the id's on the match players and
		# results would be deleted only when there wouldnt be players
		# pointing to it (zero id would have to be handled on the webby-side too)
		# but i dont want to leave zero-ids floating around, plus deleteing
		# the results by this would be kinda akward(?) and hard(?)
		
		# doh: (TODO)
		# delete from match_results where id not in
		#	(select result_id from match_players where rating_id!=0)
		
		_cursor.close()
		self.setNextUpdate( self.time() + self.UPDATE_INTERVAL )
		
###################
# maintainer makes sure theres something to do
class Maintainer( cutepig.task.SingletonTask ):
	_instance = None
	def __init__(self, app):
		cutepig.task.SingletonTask.__init__(self)
		
		self._app = app
		
	# currently use as a dummy to signal that other stuff is happening
	def run(self,args):
		#log.log("Maintainer..")
		
		# one thing the maintainer could do is to delete all of those serverinfo_players
		# that dont have a valid serverinfo pointing anymore..
		
		# ok, thats dealt with now but what we'd need is to remove old players
		# from 'ratings' that havent played in X time and also their games
		self.setNextUpdate( self.time() + 5 )
	
###################
#
# Main
