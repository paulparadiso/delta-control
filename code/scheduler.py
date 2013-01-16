from singleton import Singleton
import threading
import redis
import time
import socket

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

class ScheduleManager(threading.Thread):

	def __init__(self):
		print "initing sc."
		super(ScheduleManager, self).__init__()
		self.host = '127.0.0.1'
		self.s_port = 34311
		self.r_port = 34310
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.host, self.r_port))
		self.sock.setblocking(0) 
		self.sItems = []
		self.redis = redis.Redis()
		self.scheduleTag = 'scheduledItem'
		self.time_of_last_update = 0.0
		self.check_delay = 0.001
		self.bRunning = True

	def run(self):
		print "thread started."
		while(self.bRunning == True):
			print "running"
			#now = time.clock()
			#print now
			#diff = now - self.time_of_last_update
			#print diff
			#if diff > self.check_delay:
			#	print "timer"
			self.print_time()
			#elf.time_of_last_update = now;
			self._check_db()
			time.sleep(30.0)

	def stop(self):
		self.bRunning = False

	def _get_time_string(self):
		now = time.localtime()
		if now.tm_mon < 10:
			mon_str = "0" + str(now.tm_mon)
		else:
			mon_str = str(now.tm_mon)
		if now.tm_mday < 10:
			day_str = "0" + str(now.tm_mday)
		else:
			day_str = str(now.tm_mday)
		if now.tm_hour < 10:
			hour_str = "0" + str(now.tm_hour)
		else:
			hour_str = str(now.tm_hour)
		if now.tm_min < 10:
			min_str = "0" + str(now.tm_min)
		else:
			min_str = str(now.tm_min)
		return mon_str + '/' + day_str + '/' + str(now.tm_year) + ':' + hour_str + ':' + min_str

	def print_time(self):
		t = self._get_time_string()
		print t

	def _check_db(self):
		t_string = self._get_time_string()
		db_query = "scheduledItem:" + t_string
		print("checking for scheduled playlist - " + db_query)
		query_results = self.redis.keys(db_query)
		if(len(query_results) > 0):
			playlist = self.redis.get(query_results[0])
			play_cmd = '/play/' + playlist
			print "playing " + playlist
			self.redis.delete(query_results[0])
			self.sock.sendto(play_cmd,(self.host, self.s_port))

