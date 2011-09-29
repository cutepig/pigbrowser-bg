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

import os
import fcntl
import errno

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

# thanks to Max Polk http://code.activestate.com/recipes/576891/

class ApplicationLock:
	def __init__ (self, lockfile):
		self.lockfile = lockfile
		self.lockfd = None

	def lock (self):
		try:
			self.lockfd = os.open (self.lockfile,
								   os.O_TRUNC | os.O_CREAT | os.O_RDWR)

			# Acquire exclusive lock on the file, but don't block waiting for it
			fcntl.flock (self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)

			# Writing to file is pointless, nobody can see it
			os.write (self.lockfd, "My Lockfile")

			return True
		except (OSError, IOError), e:
			# Lock cannot be acquired is okay, everything else reraise exception
			if e.errno in (errno.EACCES, errno.EAGAIN):
				return False
			else:
				raise

	def unlock (self):
		try:
			# FIRST unlink file, then close it.  This way, we avoid file
			# existence in an unlocked state
			os.unlink (self.lockfile)
			# Just in case, let's not leak file descriptors
			os.close (self.lockfd)
		except (OSError, IOError), e:
			# Ignore error destroying lock file.  See class doc about how
			# lockfile can be erased and everything still works normally.
			pass

###################
#
# Main
