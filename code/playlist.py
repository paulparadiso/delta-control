import threading
import socket
import json

class Playlist:

	def __init__(self, input = None):
		if not input:
			self.items = {}
		else:
			self.items = input
		self.index = 0

	def get_next_item(self):
		ret = self.items[self.index]
		self.index += 1
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

class PlaylistManager(threading.Thread):

	def __init__(self):
		super(PlaylistManager, self).__init__()
		self.r_port = 34311
		self.s_port = 34312
		self.host = '127.0.0.1'
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(self.host, self.r_port)
		self.bRunning = True
		self.current_playlist = None

	def stop(self):	
		self.bRunning = False

	def run(self):
		while(self.bRunning == True):
			self.wait_for_message()

	def start(self):
		self.bRunning = True
		super(PlaylistManager, self).start()

	def _wait_for_message(self):
		data, addr = sock.recvfrom(10000)
		if data:
			self._parse_message(data, addr)

	def _parse_message(self, data, addr = None):
		res = data.split('/')
		if(len(res) > 0):
			cat = res[0]
			cmd = res[1]
			item = res[2]
			self._process_message(cat, cmd, item)

	def _process_message(self, cat, cmd, item):
		if(cat == 'list'):
			if(cmd == 'start'):
				self._start_playlist(item)
			if(cmd == 'stop'):
				self._stop_playlist(item)
			if(cmd == 'complete'):
				self._advance_playlist(item)

	def _start_playlist(self, item):
		retr_list = self.redis.get('playlist:' + item)
		if(retr_list):
			self.playlist = Playlist(json.loads(retr_list))
			self._advance_playlist()

	def _advance_playlist(self, item):
		if not self.current_playlist:
			return
		next_item = self.current_playlist.get_next_item()
		if next_item == "__done__":
			self.current_playlist == None
			return
		self._send_playlist_item(next_item)

	def _send_playlist_item(self, item):
		msg = '/start/' + item
		self.sock.sendto(msg, (self.host, self.s_port))
