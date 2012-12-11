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
		self.check_delay = 30.0
		self.bRunning = True

	def run(self):
		print "thread started."
		while(self.bRunning == True):
			now = time.clock()
			if now - self.time_of_last_update > self.check_delay:
				#self.print_time()
				self.time_of_last_update = now;
				self._check_db()
			time.sleep(30.0)

	def stop(self):
		self.bRunning = False

	def _get_time_string(self):
		now = time.localtime()
		return str(now.tm_mon) + ':' + str(now.tm_mday) + ':' + str(now.tm_hour) + ':' + str(now.tm_min)

	def print_time(self):
		t = self._get_time_string()
		print t

	def _check_db(self):
		#print("checking for scheduled playlist.")
		t_string = self._get_time_string()
		db_query = "scheduleItem:" + t_string
		query_results = self.redis.keys(db_query)
		if(len(query_results) > 0):
			playlist = self.redis.get(query_results[0])
			play_cmd = '/play/' + playlist
			#print "playing " + playlist
			self.redis.delete(query_results[0])
			self.sock.sendto(play_cmd,(self.host, self.s_port))

