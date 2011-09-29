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

import socket, time, errno
from cutepig import *
import cutepig.log as log

#######################

## NETWORK STUFF

# TODO: wrapper for nonblocking socket (or socket for that matter)

class Socket(object):
	def __init__(self, timeout, blocking=True):
		self._socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		self._socket.settimeout(timeout)
		self._socket.setblocking(blocking)
		self._timeout = timeout
		self._blocking = blocking
		self._lastData = time.time()
		
	def send(self, packet, addr):
		self._socket.sendto( packet, ip_int_tuple_s(addr) )
		
	def get(self, bufsize=4096):
		# TODO: nonblocking + timeout + stuff -> raise socket.timeout
		if( self._blocking ) :
			r = self._socket.recv( bufsize )
			self._lastData = time.time()
			return r
		# else :
		# though case, timeout/exceptions handled on our side
		try :
			r = self._socket.recv( bufsize )
			self._lastData = time.time()
			return r
		except socket.error as err:
			if( err.errno == errno.EWOULDBLOCK ) :
				if( time.time() - self._lastData >= self._timeout ) :
					raise socket.timeout()
				return None
			# other problem, re-raise
			raise err
	
	def get2(self, bufsize=4096):
		if( self._blocking ) :
			# simple case, timeout/exceptions handled on socket-side
			r, ip = self._socket.recvfrom( bufsize )
			self._lastData = time.time()
			return ( r, ip_tuple_int_s(ip) )
		# else :
		# though case, timeout/exceptions handled on our side
		try :
			r, ip = self._socket.recvfrom ( bufsize )
			self._lastData = time.time()
			return ( r, ip_tuple_int_s(ip) )
		except socket.error as err:
			if( err.errno == errno.EWOULDBLOCK ) :
				if( time.time() - self._lastData >= self._timeout ) :
					raise socket.timeout()
				return ( None, None )
			# other problem, re-raise
			raise err
			
	# socket compatibility
	def close(self):
		self._socket.close()
		
	def fileno(self):
		return self._socket.fileno()
	
	def bind(self,addr):
		self._socket.bind(addr)
		
	# TODO: logic for settimeout/setblocking
	
#######################

def getSocket ( timeout ) :
	s = socket.socket ( socket.AF_INET, socket.SOCK_DGRAM )
	s.settimeout( timeout )
	return s
	
def sendPacket ( s, packet, addr ) :
	try :
		#log.log("sendPacket addr %s" % str( ip_int_tuple_s(addr)))
		if( isinstance(s, Socket) ) :
			s.send( packet, addr )
		else :
			s.sendto( packet, ip_int_tuple_s(addr) )
	except socket.error as err:
		log.error("cutepig.net.sendPacket: socket.error %d %s (ip %s)" % 
			( err.errno, err.strerror, ip_int_tuple_s(addr) ) )	

### 2 REDUNDANT FUNCTIONS!!

# addr in int64 format
def startConversation( packet, addr, timeout) :
	# TODO: use Socket class
	ip, port = ip_int_tuple_s ( addr )
	s = socket.socket ( socket.AF_INET, socket.SOCK_DGRAM )
	s.settimeout ( timeout )
	s.sendto ( packet, (ip,port) )
	return s

def restartConversation ( s, packet, addr ) :
	# TODO: use Socket class
	ip, port = ip_int_tuple_s ( addr )
	s.sendto ( packet, (ip,port) )
	return s
	
	
def getResponse ( s, bufsize=4096 ) :
	if( isinstance(s, Socket) ) :
		return s.get(bufsize)
	else :
		return s.recv ( bufsize )

# convert address to int64 ??	
def getResponse2 ( s, bufsize=4096 ) :
	if( isinstance(s, Socket) ) :
		return s.get2( bufsize )
	else :
		r, ip = s.recvfrom ( bufsize )
		return ( r, ip_tuple_int_s(ip) )
	
# returns string format address in int64 format
def resolveHostname ( s ) :
	if ( ':' in s ) :
		ip, port = s.split(':', 1)
		port = safeint( port, 0 )
	else :
		ip = s
		port = 0
		
	if ( not is_ip ( ip ) ) :
		ip = socket.gethostbyname(ip)
		
	return ip_tuple_int ( (ip_str_int(ip), port ) )
