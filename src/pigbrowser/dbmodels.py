#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 22.5.2011

@author: hc
'''

###################
#
# Imports

import re
from cutepig.database import TableBase
import cutepig.log as log

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
	
## SERVERINFO's

class ServerPlayer ( TableBase ) :
	tablename = 'serverinfo_players'
	schema = '''
		id INT(11) NOT NULL AUTO_INCREMENT,
		server_id INT(11),
		team INTEGER,
		score INTEGER,
		ping INTEGER,
		name VARCHAR(64),
		updateround INTEGER,
		
		PRIMARY KEY(id),
		KEY key_server(server_id)
	'''
	
	def __init__(self, d = None):
		self.id = 0
		self.server_id = 0
		self.team = 0
		self.score = 0
		self.ping = 0
		self.name = ''
		self.updateround = 0

		if( d ) :
			self.fromDict(d)
			
	# from qutils dict
	def fromDict(self, d):
		self.team = d['team']
		self.score = d['score']
		self.ping = d['ping']
		self.name = d['name'][0:64]
	
# FIXME: flags as separate TINYINT(1)
class ServerInfo ( TableBase ) :
	tablename = 'serverinfos'
	schema = '''
		id INT(11) NOT NULL AUTO_INCREMENT,
		address BIGINT,
		address2 VARCHAR(64),
		name VARCHAR(64),
		sortname VARCHAR(64),
		location CHAR(2),
		continent CHAR(2),
		mapname VARCHAR(32),
		numplayers INTEGER,
		numspecs INTEGER,
		maxclients INTEGER,
		gamename VARCHAR(32),
		flags INTEGER,
		timestamp DATETIME,
		updateround INTEGER,
		skilllevel INTEGER,
		
		PRIMARY KEY(id),
		KEY key_address(address),
		KEY key_continent(continent),
		KEY key_numplayers(numplayers),
		KEY key_cont_nump(continent,numplayers),
		KEY key_cont_nump_sort(continent,numplayers,sortname)
	'''
	
	def __init__(self, d = None):
		self.id = 0
		self.address = 0
		self.address2 = 0
		self.name = ''
		self.sortname = ''
		self.location = ''
		self.continent = ''
		self.mapname = ''
		self.numplayers = 0
		self.numspecs = 0
		self.maxclients = 0
		self.gamename = ''
		self.flags = 0
		self.timestamp = None
		self.updateround = 0
		self.skilllevel = 0
		self.players = []
	
		if( d ) :
			self.fromDict(d)
			
	def fromDict(self, d):
		# TODO: clamp the names to their maximum sizes
		# Theres sometimes strange excessive amounts of whitespace
		# in some server names.. please remove them!!
		
		# DEBUG:
		if( not 'rules' in d ) :
			log.log( "NO RULES IN: %s" % d )
			
		# ch : added strip..
		name = d['name'].strip()
		self.name = name[0:128]					# 128
		self.mapname = d['map'][0:32]			# 32
		self.maxclients = d['maxp']			# actually the number of ckueb
		self.gamename = d['mod'][0:32]		# 32
		self.flags = d['flags']
		
		# ch : added sortname, only alphabetical characters
		pattern = re.compile('[\W_]+')
		self.sortname = pattern.sub('', name)
		
		if ( 'rules' in d and 'sv_skilllevel' in d['rules'] ) :
			self.skilllevel = d['rules']['sv_skilllevel']
		else :
			self.skilllevel = -1
			
		# TODO: return qi + players
		
		# the number of players is # of in-game players
		# not the spectators
		n = 0
		if( 'players' in d ) :
			for pl in d['players'] :
				if ( pl['team'] > 1 ) :
					n += 1
					
		self.numplayers = n
		self.numspecs = d['nump'] - n
		
#### RATING DATA

class PlayerRating ( TableBase ) :
	tablename = 'ratings'
	schema = '''
		id INT(11) NOT NULL AUTO_INCREMENT,
		name VARCHAR(64),
		numgames INTEGER,
		wins INTEGER,
		losses INTEGER,
		ties INTEGER,
		kills INTEGER,
		deaths INTEGER,
		lastgame DATETIME,
		rating DECIMAL(8,4),
		
		PRIMARY KEY(id),
		KEY key_rating(rating)
	'''
	# TODO: add key_rating_name ^^
	
	def __init__(self, _tuple=None):
		self.id = 0
		self.name = ''
		self.numgames = 0
		self.wins = 0
		self.losses = 0
		self.ties = 0
		self.kills = 0
		self.deaths = 0
		self.lastgame = None
		self.rating = 0.0
		
		if(_tuple):
			self.fromTuple(_tuple)
					
	def fromTuple(self, _tuple):
		self.id = _tuple[0]
		self.name = _tuple[1]
		self.numgames = _tuple[2]
		self.wins = _tuple[3]
		self.losses = _tuple[4]
		self.ties = _tuple[5]
		self.kills = _tuple[6]
		self.deaths = _tuple[7]
		self.lastgame = _tuple[8]
		self.rating = float(_tuple[9])

class MatchPlayer( TableBase ):
	tablename = 'match_players'
	schema = '''
		id INT(11) NOT NULL AUTO_INCREMENT,
		rating_id INT(11),
		result_id INT(11),
		name VARCHAR(64),
		score INTEGER,
		rating DECIMAL(8,2),
		delta DECIMAL(8,2),
		
		PRIMARY KEY(id),
		KEY key_rating(rating_id),
		KEY key_result(result_id)
	'''
	
	def __init__(self):
		self.id = 0
		self.rating_id = 0
		self.result_id = 0
		self.name = ''
		self.score = 0
		self.rating = 0.0
		self.delta = 0.0
		
class MatchResult( TableBase ) :
	tablename = 'match_results'
	schema = '''
		id INT(11) NOT NULL AUTO_INCREMENT,
		matchtime DATETIME,
		overtime TINYINT(1),
		reliable TINYINT(1),
		address BIGINT,
		location VARCHAR(2),
		mapname VARCHAR(32),
		
		PRIMARY KEY(id)
	'''
	
	def __init__(self):
		self.id = 0
		self.matchtime = None
		self.overtime = 0
		self.reliable = 0
		self.address = 0
		self.location = ''
		self.mapname = ''
		
###################
#
# Main