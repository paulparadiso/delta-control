import threading
import socket
import json
import select
import time
import redis
import settings

class Playlist:

	def __init__(self, input = None):
		self.redis = redis.Redis()
		if not input:
			self.items = []
		else:
			self.items = input
		self.index = 0

	def get_next_item(self):
		ret = '__done__'
		if self.index < len(self.items):
			ret = self.redis.get("cue:" + self.items[self.index])
			self.index += 1
		print "returning - " + ret
		return ret

	def reset(self):
		self.index = 0

	def set_item(self, index, item):
		self.items[index] = item

	def get_item(self, index):
		try:
			ret = self.items[index]
		except KeyError:
			ret = ""
		return ret

	def get_all_items(self):
		return self.items

	def make_playlist_from_json(self, j_list):
		pass

class PlaylistManager(threading.Thread):

	def __init__(self):
		super(PlaylistManager, self).__init__()
		self.r_port = settings.addresses['self']
		#self.s_port = 34312
		self.host = '127.0.0.1'
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.setblocking(0)
		self.sock.bind((self.host, self.r_port))
		self.sock.settimeout(0.1)
		self.bRunning = True
		self.current_playlist = None
		self.redis = redis.Redis()

	def stop(self):	
		self.bRunning = False

	def run(self):
		print "playlist manager awake and listening."
		while(self.bRunning == True):
			try:
				self._wait_for_message()
			except socket.timeout:
				time.sleep(0.1)


	def start(self):
		self.bRunning = True
		super(PlaylistManager, self).start()

	def _wait_for_message(self):
		data, addr = self.sock.recvfrom(10000)
		if data:
			print "got message - " + data
			self._parse_message(data, addr)
		#ready = select.select([self.sock], [], [], 1.0)
		#if ready:
		#	data = self.sock.recv(10000)

	def _parse_message(self, data, addr = None):
		if '/' in data:
			res = data.split('/')
			if(len(res) > 0):
				cmd = res[0]
				item = res[1]
				self._process_message(cmd, item)

	def _process_message(self, cmd, item):
		if(cmd == 'start'):
			self._start_playlist(item)
		if(cmd == 'stop'):
			self._stop_playlist(item)
		if(cmd == 'complete'):
			self._advance_playlist(item)

	def _start_playlist(self, item):
		print "starting playlist - " + item
		retr_list = self.redis.get('playlist:' + item)
		if(retr_list):
			self.current_playlist = Playlist(json.loads(retr_list))
			self._advance_playlist()

	def _advance_playlist(self):
		if not self.current_playlist:
			return
		next_item = self.current_playlist.get_next_item()
		if next_item == "__done__":
			self.current_playlist == None
			return
		self._send_playlist_item(next_item)

	def _send_playlist_item(self, item):
		#msg = '/start/' + item
		print "sending cues - " + item
		messages = item.split(':')
		ribbon_msg = settings.commands['goto'] % (messages[0])
		self.sock.sendto(ribbon_msg, settings.addresses['ribbon'])
		if len(messages) > 1:
			concierge_msg = settings.commands['goto'] % (messages[1])
			self.sock.sendto(concierge_msg, settings.addresses['concierge'])
