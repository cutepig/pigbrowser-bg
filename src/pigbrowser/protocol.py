#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 19.5.2011

@author: hc

protocol.py implements a protocol class that can be used to fetch serverlist from masterserver,
or serverinfo from servers.
usage:
	wsw = protocol.WarsowProtocol()
	query = protocol.ServerQuery( socket, ip, wsw )
	query.startMasterQuery ( FULLEMPTY=True, gametype='duel' ) :
	while( not query.checkMasterQuery() ) :
		sleep( sleeptime )	# wait for response from the server
		
	ips = query.finishMasterQuery()
	
	for ip in ips :
		query = protocol.ServerQuery( socket, ip, wsw )
		query.startServerQuery( fullinfo=True )
		while( not query.checkServerQuery() ) :
			sleep( sleeptime )	# wait for response from the server
			
		info = query.finishServerQuery()
		
	!! ADDED !!
	query.flushMasterQuery() - returns current list of ip's so it can be
	used sorta like an iterator object.
'''

###################
#
# Imports

import string, re, struct, datetime
import socket	# for network byte translations

import cutepig.net
import cutepig.log as log
from cutepig import *
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

# removes excessive whitespaces, strings like
# 	'server      xxxx      yeah yeah'
# get turned into
#	'server xxxx yeah yeah'

def removeWhitespace( s ) :
	return re.sub(r'\s\s+', ' ', s)

###################
#
# Classes

# query class

# TODO: change the socket into cutepig.net.Socket
class ServerQuery :

	def __init__( self, soc, addr, proto ) :
		self.socket = soc
		self.addr = addr
		self.proto = proto
		self.requestTime = None
		self.retries = -1
		
		self.error = False
		
		# response (protocol can freely "mutilate"
		# buffers field for whatever it wants
		
		self.buffers = []
		
		# stage can be "mutilated" too.. say halflife
		# flags for "got players", "got rules" etc..
		self.stage = 0
		
		# parent module can calculate traffic with this
		self.incoming = 0
		self.outgoing = 0
		
	def fileno( self ) :
		return self.socket.fileno()
	
	def startMasterQuery( self, FULLEMPTY=False, gametype=None ) :
		self.proto.startMasterQuery( self, FULLEMPTY, gametype )
		return self
		
	def checkMasterQuery( self ) :
		return self.proto.checkMasterQuery( self )
	
	def flushMasterQuery( self ):
		return self.proto.flushMasterQuery( self )
	
	def finishMasterQuery( self ) :
		return self.proto.finishMasterQuery( self )
		
	def startServerQuery( self, fullinfo=False ) :
		self.proto.startServerQuery( self, fullinfo )
		return self
		
	def checkServerQuery( self ) :
		return self.proto.checkServerQuery( self )
	
	def finishServerQuery( self ) :
		return self.proto.finishServerQuery( self )

class WarsowProtocol:
	
	masterResponse = '\xff\xff\xff\xffgetserversResponse\\'
	# put the \\ to skip it to ease the splitting
	# INFO is the short and STATUS is the long information
	statusResponse = '\xff\xff\xff\xffstatusResponse\n\\'
	infoResponse = '\xff\xff\xff\xffinfoResponse\n\\'
	
	statusQuery = '\xff\xff\xff\xffgetstatus\n'
	infoQuery = '\xff\xff\xff\xffgetinfo\n'

	# "Quick browse"
	masterQueryBase = '\xff\xff\xff\xffgetservers Warsow'
	masterQueryProtocol = '12 11'
	
	mapNames = {}
	
	def __init__( self ) :
		self.regexp = re.compile ( '\^.')

	###############################################
	####
	####
	####		WARSOW STUFF / HELPERS
	####
	####
	###############################################
		
	####################################################
	
	def supportsGametype ( self ) :
		return True
		
	# only in Q3 protocols
	def parsePlayer ( self, playerstr ) :
		d = {}
		s = playerstr.split ( '"' )
				
		# s[0] = score ping
		# s[1] = playername
		# s[2] = team (0=spec, 1=noteam, 2=red, 3=blue, 4=green, 5=yellow)
		
		if ( len ( s ) < 3 ) :
			return None
			
		s0 = s[0].split(' ')
		d['score'] = safeint(s0[0])
		d['ping'] = safeint(s0[1])
						
		d['name'] = self.string(s[1])# unicode("".join ( worklist ))
		
		# we'd need to unify this team thing too?
		d['team'] = safeint(s[2].strip())
		
		return d
		
	# split the "rulestring" into key,value pairs
	# this is not overloaded most likely
	def getRules ( self, rulestr ) :
	
		# the "rulestring" is divided with backward-slashes
		# and they are just key-value pairs, there should
		# be even amount of these
		
		split = rulestr.split ( '\\' )
		
		# now its list of [ key, value, key, value.. ]
		if ( len(split) & 1 ) :
			log.log( "uneven amount in rules?" )
			
		# key\\value\\key\\value[0x0a]
		rules = {}
		for i in range(0,len(split),2 ) :
			rules[split[i].lower()] = self.string(split[i+1])
			
		return rules
	
	# most likely not overloaded
	def getMapname ( self, mapname ) :
	
		mapname = mapname.lower()
		if ( mapname in self.mapNames ) :
			return self.mapNames[mapname]
			
		# we can beautify the mapname by removing _
		# characters and turn them to space and then
		# change the following letter to Big one
		return mapname

	# this is prolly redundant since we most likely
	# just use the modname itself ?
	def getGamename ( self, rules ) :
	
		# choose 'game' or 'gamename' ?
		mod = rules.get ( 'game', None )
		if ( not mod ) :
			mod = rules.get ( 'gamename', u'Unknown' )
			
		return mod

	# WARSOW
	def getGametype ( self, rules ) :
		if ( 'g_gametype' in rules ) :
			gt = rules.get ( 'g_gametype' )
		else :
			gt = rules.get ( 'gametype', '' )
			
		# warsow already has this as string !!
		return gt

	def getiGametype ( self, rules ) :
		# no such thing in warsow, sorry
		return 0
		
	# WARSOW
	def getFlags ( self, rules ) :
		flags = 0
		
		if ( safeint( rules.get ( 'g_needpass', 0 ) ) ) :
			flags |= FLAG_PASSWORD
		if ( safeint( rules.get ( 'g_antilag', 0 ) ) ) :
			flags |= FLAG_ANTILAG
		if ( safeint( rules.get ( 'sv_pure', 0 ) ) ) :
			flags |= FLAG_PURE
		if ( safeint( rules.get ( 'g_instagib', 0 ) ) ) :
			flags |= FLAG_INSTAGIB
		if ( safeint( rules.get ( 'sv_bots', 0 ) ) ) :
			flags |= FLAG_BOTS
		if ( safeint( rules.get ( 'bots', 0 ) ) ) :
			flags |= FLAG_BOTS
		#if ( ch_int ( rules.get ( 'g_friendlyfire', 0 ) ) ) :
		#	flags |= qutils.FLAG_FRIENDLY_FIRE
		#if ( ch_int ( rules.get ( 'sv_punkbuster', 0 ) ) ) :
		#	flags |= qutils.FLAG_ANTICHEAT
					
		return flags

	# WARSOW (same as Q3)
	def string ( self, s ) :	
		# remove color codes
		s = self.regexp.sub ( '', s )
		
		# FINALLY IT FUCKING WORKS !!!
		try : s = s.decode ( 'utf8','ignore' )
		except UnicodeDecodeError as err :
			"""
			# write this shit down
			fp = open ( NAMEFILE, 'a' )
			fp.write ( s )
			fp.write ( '\n' )
			fp.close ()
			"""
			return '(invalid encoding)'
			
		return removeWhitespace ( s )
		
	##########################################
	#
	#				WARSOW
	#			QUICK INFO OBJECTS
	#
	##########################################

	# THESE DONT GO DOWN TO URBAN TERROR BECAUSE
	# OF THE Q3UT EXCLUSION CLAUSE!

	# statusResponse
	def fullInfo ( self, rules, players ) :
		qi = {}
				
		qi['name'] = rules.get('sv_hostname', u'Unknown')
		qi['addr'] = 0	# i dont know this in here
		qi['nump'] = len(players)
		qi['maxp'] = safeint(rules.get( 'sv_maxclients', 0))
		
		mapname = rules.get('mapname', u'Unknown')
		qi['map'] = self.getMapname ( mapname )
		qi['loc'] = ''	# dont know this in here..
				
		qi['flags'] = self.getFlags ( rules )
		qi['mod'] = self.getGamename ( rules )
		qi['gt'] = self.getGametype ( rules )
		qi['igt'] = self.getiGametype ( rules )
					
		qi['rules'] = rules
		qi['players'] = players
		
		# WARSOW special - bots or not bots?
		# better to do this so that we count possible
		# specbots and if it matches the count on 'bots'
		# then we dont have bots ingame.. since some
		# bots may have ping>0 if there is latency or smt
		
		# 'esport TV'
		if ( 'bots' in rules ) :
			bots = safeint( rules['bots'], 0 )
			if ( bots ) :
				numbots = 0
				for pl in players :
					#if ( abs(pl['ping']) <= 1 and pl['team'] == 0 ) :
					#	numbots += 1
					
					# TODO : add more known tvspec names here
					if ( pl['name'] == 'esport TV' ) :
						numbots += 1
						
				if ( numbots >= bots ) :
					# tv spectator
					qi['flags'] &= ~FLAG_BOTS
					qi['rules']['bots'] = '0'
					
				"""
				reallyhasbots = False
				# check to see if bots are really playing?
				for pl in players :
					if ( abs(pl['ping']) <= 1 and pl['team'] > 0 ) :
						reallyhasbots = True
						break
						
				if ( not reallyhasbots ) :
					qi['flags'] &= ~qutils.FLAG_BOTS
					qi['rules']['bots'] = '0'
				"""
		
		return qi
		
	# from infoResponse, this is faster but doesnt list players
	# more like a "header" like thing but is enough for listview
	def quickInfo ( self, rules ) :
		qi = {}
		# ehm.. urbanterror uses this function too..
		mod = self.getGamename ( rules )
		if ( 'q3ut' in mod[0:4] ) :
			# log.log( "another ut4" )
			return None
		
		qi['name'] = rules.get('sv_hostname', u'Unknown')
		qi['addr'] = 0	# i dont know this in here
		qi['nump'] = safeint(rules.get('clients',0))
		qi['maxp'] = safeint(rules.get( 'sv_maxclients', 0))
		
		mapname = rules.get('mapname', u'Unknown')
		qi['map'] = self.getMapname ( mapname )
		qi['loc'] = ''	# dont know this in here..
		
		qi['mod'] = self.getGamename ( rules )
		qi['gt'] = self.getGametype ( rules )
		qi['igt'] = self.getiGametype ( rules )
			
		# warsow has interesting quirk: sv_skilllevel.. should add this here somehow?
		
		# no need for this in Warsow	
		"""
		# hack the flags in like this
		if ( 'pure' in rules ) :
			rules['sv_pure'] = rules['pure']
		if ( 'needpass' in rules ) :
			rules['g_needpass'] = rules['needpass']
		if ( 'punkbuster' in rules ) :
			rules['sv_punkbuster'] = rules['punkbuster']
		if ( 'friendlyfire' in rules ) :
			rules['g_friendlyfire'] = rules['friendlyfire']
		if ( 'balancedteams' in rules ) :
			rules['g_balancedteams'] = rules['balancedteams']
		"""
		# weaprestrict -> g_heavyweaponrestriction ??
			
		qi['flags'] = self.getFlags( rules )
		
		# we dont return even the rules in quickinfo!
		# qi['rules'] = rules

		return qi
		
	######################################		
	####
	####			QUAKE III
	####		
	####
	######################################
	
	# common	
	def checkMasterResponse ( self, packet ) :
		lr = len( self.masterResponse )
		if( self.masterResponse not in packet[0:lr] ) :
			return -1
			
		return lr
	
	# game specific	
	def checkServerResponse ( self, packet, isfull ) :
		if ( isfull ) :
			q = self.statusResponse
		else :
			q = self.infoResponse
			
		lr = len ( q )
		if ( q not in packet[0:lr] ) :
			return -1
			
		return lr

	####################################################
	#
	#				QPROTOCOL
	#			SERVER REQUESTS
	#
	####################################################
	
	# game specific
	def startServerQuery ( self, query, fullinfo=False ) :
			
		if ( fullinfo ) :
			q = self.statusQuery
			query.isfull = True
		else :
			q = self.infoQuery
			query.isfull = False
			
		cutepig.net.sendPacket ( query.socket, q, query.addr )
		query.requestTime = datetime.datetime.now ()
		query.retries += 1
		
		query.outgoing += len ( q )
		
		return query
	
	# common for all Quakes	
	def checkServerQuery ( self, query ) :
		try :
			r, addr = cutepig.net.getResponse2 ( query.socket )
		except :
			return True
		if( not r and not addr ) :
			return False
		query.incoming += len ( r )
		if ( addr != query.addr ) :
			log.log( "Warning: getting response2 from different address??" )
			return False
	
		# quake doesnt need no stinking stages
		query.buffers.append ( r )
		return True
		
	# common for all Quakes
	def finishServerQuery ( self, query ) :
		# do the parsing thing
		if ( len(query.buffers) ) :
			ofs = self.checkServerResponse ( query.buffers[0], query.isfull )
			if ( ofs == -1 ) :
				log.log( "getInfos, malicious packet from %s" % ( ip_int_str_full(query.addr) ) )
				# if ( not return_timeouts ) :
				#	return None
				info = { 'addr' : query.addr, 'error' : 1 }
				return info	# or None

			i = self.parseServerResponse ( query.buffers[0][ofs:], query.isfull )
			if ( i ) :
				i['addr'] = query.addr
				# if ( query.gametype and query.gametype != i['gt'] ) :
				#	return None
				
			return i
			
		else :
			info = { 'addr' : query.addr, 'timeout' : 1 }
			return info # or None
		
	####################################################
	#
	#					WARSOW
	#				MASTER REQUESTS
	#
	####################################################	
		
	# "Quick browse" mode for Q3+ engines
	def startMasterQuery ( self, query, FULLEMPTY=False, gametype=None ) :
		# form the query packet
		q = '%s %s' % ( self.masterQueryBase, self.masterQueryProtocol )
		if ( gametype ) :
			q += ' gametype=%s' % gametype
		if ( FULLEMPTY ) :
			q += ' full empty'
		
		cutepig.net.sendPacket( query.socket, q, query.addr )
		query.requestTime = datetime.datetime.now ()
		query.retries += 1
		
		query.outgoing += len ( q )
		
		return query

	# common for all Quakes
	def checkMasterQuery( self, query ) :
		# FIXME: add internal asynchronous timeout to support nonblocking sockets!
		# this relying on timeout dont work well in new pigbrowser taskmanager..
		try :
			r, addr = cutepig.net.getResponse2 ( query.socket )
			if( not r and not addr ) :
				return False
			query.incoming += len ( r )
			if ( addr != query.addr ) :
				log.log( "Warning: getting response2 from different address??" )
				return False
			
			ofs = self.checkMasterResponse ( r )
			if ( ofs == -1 ) :
				log.log( "Malicious packet from master %s" % ( cutepig.ip_int_str_full(query,addr) ) )
				query.error = True
				return True
				
			# master server query stores the ip's in the buffer directly
			ips = self.parseMasterResponse ( r[ofs:] )
			if ( not len(ips) ) :
				log.log( "Empty ip list from master %s %s" % ( cutepig.ip_int_str_full(query.addr), r ) )
				return True	# dont take as error?
				
			else :
				# log.log( "Read %d ips (last %s)" % (len(ips), ips[-1]) )
				query.buffers.extend ( ips )
				
		except socket.timeout :
			if ( not len(query.buffers) ) :
				log.log( "Master server %s timeouted" % ( cutepig.ip_int_str_full(query.addr) ) )
				
			return True	# we can stop now (quake specific: timeout=no more data)
			
		return False	# keep going badass
	
	# used to fetch gathered list of ips
	def flushMasterQuery( self, query ):
		buffers = self.query.buffers
		# create a new buffer so above references to old valid buffer
		self.query.buffers = []
		return buffers
	
	# common for all Quakes
	def finishMasterQuery ( self, query ) :
		return query.buffers
	
	####################################################
	#
	#				QUAKE III
	#		RESPONSE PARSING - MASTER + SERVER
	#
	####################################################
	
	# game specific
	def parseMasterResponse ( self, buf ) :
		# Q3:n formaatti: header \ 6 bytes \ 6 bytes
		ln = len(buf)
		next = 0
		ips = []
		
		next = buf.find ( '\\', next )	
		while ( next < (ln-6) and next >= 0 ) :
			if ( "EOT\0\0\0" in buf[next+1:next+7] ) :
				break
			
			ip = socket.ntohl( struct.unpack( 'I', buf[next+1:next+5] )[0] )
			p = socket.ntohs( struct.unpack( 'H', buf[next+5:next+7])[0] )
			# yield ip_tuple_int ( (ip,p) )
			ips.append ( ip_tuple_int((ip,p)) )
			
			next = buf.find( '\\', next + 1)
		
		return ips
		
	#
	# QUAKE III
	#
	def parseServerResponse ( self, buf, isfull ) :
		ls = buf.split ( '\x0a' )
		if ( len(ls) < 1 ) :
			log.log( 'empty server response??\n%s' % buf )
			return None
			
		rules = self.getRules ( ls[0] )
		
		players = []
		# number score time ping "name" "skin" color1 color2
		if (isfull and len(ls) > 1 ) :
			for player in ls[1:] :
				player = player.strip()
				if ( len(player) <= 1 ) :
					continue
				d = self.parsePlayer ( player )
				if ( d ) :
					players.append ( d )
		
		if ( isfull ) :
			return self.fullInfo ( rules, players )
		else :
			return self.quickInfo ( rules )

###################
#
# Main
