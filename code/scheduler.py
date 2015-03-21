from singleton import Singleton
import threading
import redis
import time
import datetime
import socket
import settings

class ScheduledItem:

	def __init__(self):
		self.time = time
		self.playlist = playlist

	def set_time(self, time):
		self.time = time

	def set_playlist(self, playlist):
		self.playlist = playlist

	def get_time(self):
		return self.time

	def get_playlist(self):
		return self.playlist
#####
#
# Manage scheduled items.  New scheduled items are saved by the main server in delta.py.
# Check for scheduled items every minutes and launch if they exist.
#
#####

class ScheduleManager:

	def __init__(self):
		print "initing sc."
		#super(ScheduleManager, self).__init__()
		self.host = '127.0.0.1'
		self.s_port = settings.addresses['self']
		print "scheduler setting port to " + str(self.s_port)
		self.r_port = 34310
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.bind((self.host, self.r_port))
		self.sock.setblocking(0) 
		self.sItems = []
		self.redis = redis.Redis()
		self.scheduleTag = 'scheduledItem'
		self.time_of_last_update = 0.0
		self.check_delay = 0.001
		self.bRunning = True
		self.b_have_new_playlist = False
		self.new_playlist = ''
		self.next_update = datetime.datetime.now() - datetime.timedelta(minutes = 10)
		
	def run(self):
		print "thread started."
		while(self.bRunning == True):
			#print "running"
			#now = time.clock()
			#print now
			#diff = now - self.time_of_last_update
			#print diff
			#if diff > self.check_delay:
			#	print "timer"
			#self.print_time()
			#self.sock.sendto("checking for get_playlist",(self.host, self.s_port))
			#elf.time_of_last_update = now;
			#self._check_db()
			#time.sleep(60.0)
			pass

	#Update.  Get the current time and check if there is a corresponding item in the database.
			
	def update(self):
		now = datetime.datetime.now()
		if now > self.next_update:
			self._check_db()
			self.next_update = now + datetime.timedelta(seconds = 60)
			
	def stop(self):
		self.bRunning = False

	#Convert the datetime string to a javascript compatible date string.

	def _get_time_string(self, future = False):
		now = datetime.datetime.now()
		if future:
			now = now + datetime.timedelta(minutes = 15)
		if now.month < 10:
			mon_str = "0" + str(now.month)
		else:
			mon_str = str(now.month)
		if now.day < 10:
			day_str = "0" + str(now.day)
		else:
			day_str = str(now.day)
		if now.hour < 10:
			hour_str = "0" + str(now.hour)
		else:
			hour_str = str(now.hour)
		if now.minute < 10:
			min_str = "0" + str(now.minute)
		else:
			min_str = str(now.minute)
		return mon_str + '/' + day_str + '/' + str(now.year) + ':' + hour_str + ':' + min_str

	def print_time(self):
		t = self._get_time_string()
		print t

	def have_new_playlist(self):
		return self.b_have_new_playlist
		
	def get_new_playlist(self):
		self.b_have_new_playlist = False
		return self.new_playlist
	
	#####
	#
	# Check to see if there is going to be a scheduled item soon.  If so send 
	# out the power on command.
	#
	#####

	def _check_future(self):
		t_string = self._get_time_string(future = True)
		db_query = "scheduledItem:" + t_string
		query_results = self.redis.keys(db_query)
		if(len(query_results) > 0):
			playlist = 'Power On'
			play_cmd = 'start/' + playlist
			print "scheduler sending " + playlist
			#self.redis.delete(query_results[0])
			#self.sock.sendto(play_cmd,settings.addresses['self'])
			self.new_playlist = play_cmd
			self.b_have_new_playlist = True

	#Get the current timestring and check the database for a scheduled item with that time.

	def _check_db(self):
		t_string = self._get_time_string()
		db_query = "scheduledItem:" + t_string
		print("checking for scheduled playlist - " + db_query)
		query_results = self.redis.keys(db_query)
		if(len(query_results) > 0):
			playlist = self.redis.get(query_results[0])
			if(playlist):
				play_cmd = 'start/' + playlist
				print "scheduler sending " + playlist
				#self.redis.delete(query_results[0])
				#self.sock.sendto(play_cmd,('127.0.0.1', settings.addresses['self'][1]))
				self.new_playlist = play_cmd
				self.b_have_new_playlist = True
		self._check_future()

