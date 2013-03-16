import threading
import socket
import json
import select
import time
import redis
import settings
import scheduler

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
		if ret != None:
			print "returning - " + ret
		else:
			print "returning empty item."
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
		self.check_internal = True
		#self.r_port = 34312
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.ex_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.setblocking(0)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.ex_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(settings.addresses['self'])
		#self.sock.bind(settings.addresses['self'])
		#self.ex_sock.bind(settings.addresses['self'])
		self.sock.settimeout(1.0)
		#self.ex_sock.settimeout(1.0)
		#self.ex_sock.settimeout(1.0)
		self.bRunning = True
		self.current_playlist = None
		self.redis = redis.Redis()
		self.wait_list = []
		self.sm = scheduler.ScheduleManager()
		self.new_message = None
		
	def set_message(self, message):
		self.new_message = message
		print self.new_message
		
	def stop(self):	
		self.bRunning = False

	def run(self):
		print "playlist manager awake and listening."
		default_playlist = self.redis.get('defaultPlaylist')
		self._start_playlist(default_playlist)
		self._advance_playlist()
		while(self.bRunning == True):
			try:
				self._wait_for_message()
			except socket.timeout:
				time.sleep(0.1)


	def start(self):
		self.bRunning = True
		super(PlaylistManager, self).start()

	def _check_wait_list(self, s):
		print "checking for %s in waitlist" % (s)
		for i in self.wait_list:
			print "checking %s against %s" % (s,i)
			if s in i:
				print "found wait string"
				self.wait_list.remove(i)
				print "waitlist now has %d items" % (len(self.wait_list))
				if len(self.wait_list) < 2:
					return True
					return True
		return False

	def _wait_for_message(self):
		try:
			#print "checking intenal socket"
			data = self.sock.recv(10000)
			if data:
				data = data.strip()
				print "got message - " + data
				self._parse_message(data)
		except socket.timeout:
			pass
		self.sm.update()
		if self.sm.have_new_playlist():
			plist = self.sm.get_new_playlist()
			print "received new playlist - " + plist
			self._parse_message(plist)
		if self.new_message != None:
			print "new message"
			self._parse_message(self.new_message)
			self.new_message = None
		#ready = select.select([self.sock], [], [], 1.0)
		#if ready:
		#	data = self.sock.recv(10000)

	def _parse_message(self, data, addr = None):
		if '/' in data:
			res = data.split('/')
			if(len(res) > 0):
				cmd = res[0]
				item = res[1]
				if(len(res) > 2):
					extra = res[2]
				else:
					extra = None
				self._process_message(cmd, item, extra)
			return
		if settings.commands['startup'] in data:
			self._advance_playlist()
			return
		if len(self.wait_list) > 0:
			if self._check_wait_list(data):
				self._advance_playlist()
				return

	def _process_message(self, cmd, item, extra):
		if(cmd == 'start'):
			self._start_playlist(item)
			if extra != None:
				if extra == 'now':
					self._advance_playlist()
		if(cmd == 'stop'):
			self._stop_playlist(item)
		if cmd == 'cmd':
			if item == 'SKIP':
				print "playlist got skip."
				self._advance_playlist()

	def _start_playlist(self, item):
		if item == 'Power On':
			self.sock.sendto(settings.commands['power_on'], settings.addresses['crestron'])
			return
		if item == 'Power Off':
			self.sock.sendto(settings.commands['power_off'], settings.addresses['crestron'])
			return
		print "starting playlist - " + item
		retr_list = self.redis.get('playlist:' + item)
		if(retr_list):
			#self.wait_list = []
			self.current_playlist = Playlist(json.loads(retr_list))
			#self._advance_playlist()
		else:
			print "blank playlist"

	def _advance_playlist(self):
		if not self.current_playlist:
			return
		self.wait_list = []
		#for i in self.wait_list:
		#	self.wait_list.remove(i)
		next_item = None
		while next_item == None:
			next_item = self.current_playlist.get_next_item()
		if next_item == "__done__":
			default_playlist = self.redis.get('defaultPlaylist')
			self._start_playlist(default_playlist)
			self._advance_playlist()
		else:
			self._send_playlist_item(next_item)

	def _send_playlist_item(self, item):
		#msg = '/start/' + item
		print "sending cues - " + item
		messages = item.split(':')
		ribbon_msg = settings.commands['goto'] % (messages[0])
		ribbon_wait = settings.commands['wait'] % (messages[0])
		self.wait_list.append(ribbon_wait)
		print "wait_list = " + self.wait_list[0]
		self.sock.sendto(ribbon_msg, settings.addresses['ribbon'])
		if len(messages) > 1:
			concierge_msg = settings.commands['goto'] % (messages[1])
			concierge_wait = settings.commands['wait'] % (messages[1])
			self.wait_list.append(concierge_wait)
			self.sock.sendto(concierge_msg, settings.addresses['concierge'])
