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

import MySQLdb
import _mysql_exceptions

from cutepig import *
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

class TableBase(object):
	tablename = ''
	schema = ''
	
	def __init__(self):
		pass
	
	# add engine here (and charset?)
	def Create (self, cursor, engine=None, charset=None):
		s = "CREATE TABLE IF NOT EXISTS %s (%s)" % ( self.tablename, self.schema )
		if ( engine ) :
			s += " ENGINE=%s" % engine
		if ( charset ) :
			s += " DEFAULT CHARSET=%s" % charset
		cursor.execute ( s )

###################

class Database:
	def __init__(self, **args):
		# TODO: add custom parameters to args like cursor or whatnot..
		self._args= args
		self._tables = []
		self._connect()
	
	def _connect(self):
		self._conn = MySQLdb.connect(**self._args)
	
	def _testconn(self):
		try :
			self._conn.ping()
		except _mysql_exceptions.OperationalError as err:
			#if( err.args[0] == 2006 ) :
			# try to re-establish connection
			self._connect()
				
	def cursor(self):
		self._testconn()
		return self._conn.cursor()
	
	def commit(self):
		self._testconn()
		self._conn.commit()
		
	def close(self):
		self._conn.close()

	# hidden function of MySQLdb
	def insert_id(self, cursor=None):
		# TODO: execute LAST_INSERT_ID
		self._testconn()
		return self._conn.insert_id()
	
	def createTables(self, module, engine, charset, create_to_db):
		cursor = self._conn.cursor()
		for name in dir(module) :
			o = getattr( module, name )
			try:
				if( o != TableBase and issubclass(o, TableBase) ) :
					newobj = o ()
					if( not newobj.tablename in self._tables ) :
						# log.log( newobj )
						if( create_to_db ) :
							newobj.Create(cursor, engine, charset)
						self._tables[newobj.tablename] = newobj
			except TypeError :
				pass
	
###################
#
# Main
