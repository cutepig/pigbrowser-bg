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

import re
import datetime
import operator

import cutepig
import cutepig.log as log
from pigbrowser import *

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

class PlayerState:
	def __init__(self, d=None):
		self._name = ''
		self._score = 0
		self._team = 0
		
		if(d):
			self.fromDict(d)
			
	def fromDict(self, d):
		self._name = d['name']
		self._score = d['score']
		self._team = d['team']
		
###################
		
class DuelState:
	MAX_TIMEOUTS = 5
	def __init__(self, job, info):
		self._job = job
		self._valid = False
		self._reliable = False
		self._timeouts = 0
		self._matchtime = ''
		self._currtime = None
		self._timelimit = None
		self._mapname = ''
		self._overtime = False
		self._players = []
		
		if(not self._validateFields(info)):
			return
		
		self.fromDict(info)
		self._valid = True
		
	def fromDict(self,info):
		self._matchtime = info['rules']['g_match_time'].lower()
		self._currtime, self._timelimit = self._parseMatchtime(self._matchtime)
		self._overtime = 'overtime' in self._matchtime
		self._mapname = info['map']
		if('players' in info):
			for _pl in info['players']:
				if(_pl['team'] == 2 or _pl['team'] == 3):
					self._players.append(PlayerState(_pl))

	def isValid(self):
		return self._valid
	
	# returns tuple of ( current-time, timelimit )
	@staticmethod
	def _parseMatchtime(g_match_time):
		_currtime = None
		_timelimit = None
		m = re.search( '(\S+) / (\S+)', g_match_time )
		if( m != None and len( m.groups() ) == 2 ) :
			_currtime, _timelimit = [datetime.datetime.strptime(g, "%M:%S") for g in m.groups() ]
		# else:
		# log.log("parseMatchTime: failed to parse matchtime (%s)" % g_match_time)
		return _currtime, _timelimit
		
	# check for necessary fields in the info structure
	@staticmethod
	def _validateFields(info):
		flags = info['flags']
		if('timeout' in info):
			return False
		if('error' in info):
			return False
		if(not 'flags' in info):
			return False
		if(not 'map' in info):
			return False
		if(not 'gt' in info):
			return False
		if(not 'rules' in info):
			return False
		if(not 'g_match_time' in info['rules']):
			return False
		return True
	
	# check conditions for ongoing duel
	@staticmethod
	def checkActiveDuel(info):
		# validate all necessary fields that we use
		valid = True
		if(not DuelState._validateFields(info)) :
			# no-op?
			valid = False
		
		# commenting some stuff out	
		elif( info['flags'] & FLAG_INSTAGIB != 0 ) :
			valid = False
			# log.log("checkActiveDuel: FLAG_INSTAGIB")
		elif ( info['flags'] & FLAG_BOTS != 0 ) :
			valid = False
			# log.log("checkActiveDuel: FLAG_BOTS")
		elif ( info['gt'] != 'duel' ) :
			valid = False
			# log.log("checkActiveDuel: not duel")
		elif ( ('wamphi' in info['map'][0:6]) or ('maxpov' in info['map'][0:6]) ) :
			valid = False
			
		if ( valid ) :
			matchtime = info['rules']['g_match_time'].lower()
			if (matchtime not in ['finished', 'warmup', 'countdown']) :
				currtime, timelimit = DuelState._parseMatchtime(matchtime)
				# oh, we got something dude..		
				if (currtime and timelimit) :
					if(timelimit.time() != datetime.time(minute=10)):
						valid = False
						#log.log("checkActiveDuel: timelimit")
					else:
						#log.log ( "VALID matchtime: %s" % matchtime )
						return True
				
		return False
	
	# checks if current state is finished
	def checkFinished(self, last):
		if(self._matchtime == 'finished'):
			return True

		return False
		
	# checks if current state went over the end of the game
	def checkNewGame(self, last):
		if(not last):
			return False
		# first validate that the last state had a matchtime
		if(not last._currtime):
			return False
		if(last._matchtime in ['countdown', 'warmup','finished']):
			return False
		# ok, lets check if current time is something else
		if(self._matchtime in ['countdown', 'warmup']):
			log.log("DuelState::checkNewGame: matchtime @ %s" % self._matchtime)
			return True
		if(not self._currtime):
			log.log("DuelState::checkNewGame: currtime null")
			return True
		if(self._currtime < last._currtime):
			# overtime logic
			if(not self._overtime):
				log.log("DuelState::checkNewGame: currtime smaller %s %s" % (self._currtime, last._currtime))
				return True
		return False
		
	# if this returns 'False', prefer the lastState over this
	def isReliable(self):
		if(self._matchtime != 'finished'):
			log.log("DuelState::isReliable: matchtime")
			return False
		# check the score line for 0-0 bug
		if(len(self._players) != 2 ):
			log.log("DuelState::isReliable: len(players) != 2 (%d)" % (len(self._players)))
			return False
		if(self._players[0]._score == 0 and self._players[1]._score == 0):
			log.log("DuelState::isReliable: 0-0 bug")
			return False
	
		# hmm, what else	
		return True
	
	def checkRagequit(self, last):
		_ragequit = None
		if(not last):
			return None
		# find a player from last state that is missing from the new state
		for _pl in last._players:
			_found = None
			for _curr in self._players:
				if(_pl._name == _curr._name):
					_found = _pl
					break
			if(not _found):
				# we only have 1
				if(not _ragequit):
					_ragequit = _found
				else:
					# if we have more, then we have ambigious state
					# and we cant tell who if anyone ragequitted
					_ragequit = None
					break
		# fix the score to reflect ragequitting
		if(_ragequit):
			_ragequit._score = -99999
			
		return _ragequit
	
	def getRemainingSeconds(self):
		if(self._timelimit and self._currtime):
			return cutepig.total_seconds(self._timelimit - self._currtime)
		else:
			return 0.0

###################
#
# Main
