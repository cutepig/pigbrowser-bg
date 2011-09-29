#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-
'''
Created on 7.8.2011

@author: hc
'''

###################
#
# Imports

import exceptions
import sched, time
import cutepig.log as log

###################
#
# Constants

PRIORITY_NONE = -1
PRIORITY_LOW = 0
PRIORITY_MEDIUM = 1
PRIORITY_HIGH = 2
PRIORITY_EXTREME = 3

###################
#
# Globals

###################
#
# Helpers

###################
#
# Classes

class Task :
	_WARN_TIME = 0.1	# in seconds
	def __init__(self):
		self._event = None			# id for sched
		self._registered = False	# if _event is valid for _scheduler
		self._taskmanager = None	# TaskManager
	
		self._nextUpdate = 0		# as time
		self._priority = 0
		
		self._args = None			# as packed sequence
		
	def _setEvent(self, event):
		self._event = event
		
	def _getEvent(self):
		return self._event
		
	def _setTaskManager(self, taskmanager):
		self._taskmanager = taskmanager
		
	def _setJobId(self, jobid):
		self._jobId = jobid
		
	# also 'reinsert', check
	def _insertJob(self, *args) :
		if( self._taskmanager is not None ) :
			scheduler = self._taskmanager.getScheduler()
			self._event = scheduler.enterabs( self._nextUpdate, self._priority, self, args )
			self._registered = True
			# store this for 'rescheduling'
			self._args = args
	
	# cancel on scheduler and
	def _removeJob(self) :
		if( self._taskmanager and self._taskmanager.inQueue( self ) ) :
			# log.log("Task: canceled job")
			self._taskmanager.getScheduler().cancel( self._event )
		self._registered = False
	
	def _isScheduled(self) :
		return self._registered
	
	def _getNextUpdate(self):
		return self._nextUpdate
	
	def _getPriority(self):
		return self._priority
	
	# callback to sched
	def __call__(self, *args):
		t = time.time()
		self.run(args)
		d = time.time() - t
		if(d > self._WARN_TIME):
			log.log("Task::__call__: execution time took %f seconds (%s)" % (d, self.__class__.__name__))
		
		self._event = None
		# TODO: check nextupdate and stuff
		# reschedule
		if( self._registered ) :
			self._insertJob()
	
	# public functions
	def setNextUpdate(self, time):
		self._nextUpdate = time
		
	def setPriority(self, priority):
		self._priority = priority
		
	def removeSelf(self):
		if( self._taskmanager ) :
			self._taskmanager.removeJob( self )

	def time(self):
		return time.time()

	def reschedule(self):
		self._removeJob()
		self._insertJob()

	# OVERRIDE
	def run(self, args):
		pass

###################

class SingletonTask( Task ):
	# you have to implement this in your inherited class
	_instance = None
	def __init__(self):
		if( self._instance is not None ) :
			raise exceptions.Exception( "SingletonTask already instanced" )
		Task.__init__(self)
		_instance = self
		
	@classmethod
	def isInstanced(cls):
		return cls._instance is not None
	
	@classmethod
	def getInstance(cls):
		return cls._instance

###################
	
class TaskManager :
	def __init__(self):
		self._scheduler = sched.scheduler( time.time, time.sleep )
		self._jobs = []
		
	# public functions
	def addJob(self, nextUpdate, priority, job, *args):
		job._setTaskManager( self )
		job.setNextUpdate( nextUpdate )
		job.setPriority( priority )
		
		job._insertJob( args )
		self._jobs.append( job )

	def removeJob(self, job):
		# this handles the sched side
		job._removeJob()
		self._jobs.remove(job)
				
	def inQueue(self, job):
		if( not self._scheduler ) :
			return False
		
		# find the jobs id in the queue list
		queue = self._scheduler.queue
		for q in queue :
			if( q.action == job ) :
				return True
			
		return False

	def runJobs(self):
		if( self._scheduler ) :
			self._scheduler.run()

	def getScheduler(self):
		return self._scheduler

###################
#
# Main
