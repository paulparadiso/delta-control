import web
import redis
import json
import socket
import settings
from datetime import date, timedelta
from settings import commands, addresses
from playlist import PlaylistManager
from scheduler import ScheduleManager

"""
SndMsg socket for testing playlist manager.
"""

snd_msg_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
snd_msg_host = '127.0.0.1'
snd_msg_port = settings.addresses['self']
rib_sock = settings.addresses['ribbon']
con_sock = settings.addresses['concierge']

days_in_month = {
	'01':31,
	'02':29,
	'03':31,
	'04':30,
	'05':31,
	'06':30,
	'07':31,
	'08':31,
	'09':30,
	'10':31,
	'11':30,
	'12':31,
}

urls = (
	'/', 'Index',
	'/master', 'Index',
	'/control','Command',
	'/playlists','Playlists',
	'/getplaylist', 'GetPlaylist',
	'/scheduling','Scheduling',
	'/submitdate', 'Date',
	'/submitschedule', 'Date',
	'/getplaylists', 'GetPlaylists',
	'/setdefault', 'SetDefault',
	'/clips','Clips',
	'/getclips','GetClips',
	'/clearplaylists', 'ClearPlaylists',
	'/clearcues', 'ClearCues',
	'/sndmsg', "SndMsg",
)

redis = redis.Redis('localhost')

render = web.template.render('templates')
#print render.hello('world')

def clear_date(date):
	date_keys = redis.keys('scheduledItem:' + date + ":*")
	for key in date_keys:
		redis.delete(key)

class Index:

	def GET(self):
		header = render.header()
		nav = render.nav('master')
		playlist_keys = redis.keys('playlist:*')
		#playlists = ['test1','test2','test3','test4','test5']
		playlists = []
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		return render.master(header, nav, playlists)

class Scheduling:

	def GET(self):
		header = render.header()
		nav = render.nav('scheduling')
		playlist_keys = redis.keys("playlist:*")
		playlists = []
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		return render.scheduling(header, nav, playlists)

class Playlists:

	def GET(self):
		header = render.header()
		nav = render.nav('playlists')
		playlists = {}
		playlist_keys = redis.keys('playlist:*')
		cues = []
		cue_keys = redis.keys('cue:*')
		for i in cue_keys:
			cues.append(i.split(':')[1])
		print cues
		for i in playlist_keys:
			playlist_name = i.split(':')[1]
			playlist = json.loads(redis.get(i))
			playlists[playlist_name] = playlist
		return render.playlists(header, nav, playlists, cues)

	def POST(self):
		params = web.input()
		plist_name = params.name;
		plist_name = plist_name.lstrip()
		plist_name = plist_name.rstrip()
		plist_str = params.playlist
		#print "new playlist - " + plist_name
		#print plist_str
		plist = plist_str.split(":")
		del plist[-1]
		redis.set('playlist:' + plist_name, json.dumps(plist))


class Clips:

	def GET(self):
		header = render.header()
		nav = render.nav('clips')
		cue_keys = redis.keys("cue:*")
		cues = []
		for i in cue_keys:
			cues.append(i.split(':')[1])
		return render.clips(header, nav, cues)

	def POST(self):
		params = web.input()
		clipName = params.clipName
		ribbonCue = params.ribbonCue
		conciergeCue = params.conciergeCue
		#editedClip = params.editedClip
		#redis.delete('cue:' + editedClip);
		redis.set("cue:" + clipName, ribbonCue + ':' + conciergeCue)

class SndMsg:

	def GET(self):
		header = render.header()
		nav = render.nav('sndmsg')
		page = render.sndmsg(header, nav)
		return page

	def POST(self):
		params = web.input()
		msg = params.msg
		print "Sending message - " + msg
		snd_msg_sock.sendto(msg, (snd_msg_host, snd_msg_port))

class Command:
	
	def POST(self):
		#print d
		params = web.input()
		#print "got command - " + params.cmdtype + " - " + params.cmd
		if params.cmdtype == 'playlist':
			self._start_playlist(params.cmd)
		if params.cmdtype == 'control':
			self._control_cmd(params.cmd)
			
	def _start_playlist(self, plist):
		#print "starting playlist - " + plist
		play_cmd = 'start/' + plist
		snd_msg_sock.sendto(play_cmd,(snd_msg_host, snd_msg_port))

		
	def _control_cmd(self, cmd):	
		#print "sending playback command - " + cmd
		control_cmd = settings.commands[cmd]
		print "sending - " + control_cmd
		if cmd == "skip":
			snd_msg_sock.sendto(settings.addresses['self'], control_cmd)
			return
		if cmd == "power_on" or cmd == "power_off":
			snd_msg_sock.sendto(settings.addresses['self'], control_cmd)
			return
		snd_msg_sock.sendto(control_cmd, rib_sock)
		snd_msg_sock.sendto(control_cmd, con_sock)

class Date:

	def GET(self):
		params = web.input()
		date = params.date
		date_key = 'scheduledItem:' + date + ':*'
		scheduled_keys = redis.keys(date_key)
		scheduled_items = {}
		for i in scheduled_keys:
			split_key = i.split(':')
			hour = split_key[2]
			minute = split_key[3]
			playlist = redis.get(i)
			scheduled_items[hour + ':' + minute] = playlist
		return json.dumps(scheduled_items)

	def POST(self):
		params = web.input()
		print params.keys()
		date = params.date
		clear_date(date)
		print("setting schedule for " + date + " to " + params.mode)
		if(params.mode == "day"):
			self._clear_day(date)
			self._set_day(date, params)
		if(params.mode == "week"):
			self._clear_week(date)
			self._set_week(date, params)
		if(params.mode == "month"):
			self._clear_month(date)
			self._set_month(date, params)

	def _get_week_start(self, week, year):
		d = date(year, 1, 1) 	   
		delta_days = d.isoweekday() - 1
		delta_weeks = week
		if year == d.isocalendar()[0]:
			delta_weeks -= 1
		delta = timedelta(days=-delta_days, weeks=delta_weeks)
		return d + delta

	def _clear_day(self, _date):
		print "clearing " + _date
		keys = redis.keys('scheduledItem:' + _date + ':*')
		for i in keys:
			redis.delete(i)

	def _clear_week(self, _date):
		date_lst = _date.split('/')
		print "setting week of - " + _date
		week = date(int(date_lst[2]), int(date_lst[0]), int(date_lst[1])).isocalendar()[1]
		week_start = self._get_week_start(week, int(date_lst[2]))
		for i in range(0,7):
			next_date = week_start + timedelta(days=i)
			year = str(next_date.year)
			if(next_date.month < 10):
				month = "0" + str(next_date.month)
			else:
				month = str(next_date.month)
			if(next_date.day < 10):
				day = "0" + str(next_date.day)
			else:
				day = str(next_date.day)
			date_str = month + '/' + day + '/' + year
			self._clear_day(date_str)

	def _clear_month(self, _date):
		date_lst = _date.split('/')
		for i in range(1, days_in_month[date_lst[0]] + 1):
			year = date_lst[2]
			month = date_lst[0]
			day = str(i + 1)
			new_date = month + '/' + day + '/' + year
			self._clear_day(new_date)

	def _set_day(self, _date, sch):
		for key in sch.keys():
			if(key == "date" or key == "mode"):
				continue
			print "setting - " + _date
			redis.set("scheduledItem:" + _date + ":" + key, sch[key])

	def _set_month(self, _date, sch):
		date_lst = _date.split('/')
		for i in range(1, days_in_month[date_lst[0]] + 1):
			year = date_lst[2]
			if(date_lst[0] < 10):
				month = "0" + date_lst[0]
			else:
				month = date_lst[0]
			if(i < 10):
				day = "0" + str(i)
			else:
				day = str(i)
			new_date = month + '/' + day + '/' + year
			self._set_day(new_date, sch)

	def _set_week(self, _date, sch):
		date_lst = _date.split('/')
		print "setting week of - " + _date
		week = date(int(date_lst[2]), int(date_lst[0]), int(date_lst[1])).isocalendar()[1]
		week_start = self._get_week_start(week, int(date_lst[2]))
		for i in range(0,7):
			next_date = week_start + timedelta(days=i)
			year = str(next_date.year)
			if(next_date.month < 10):
				month = "0" + str(next_date.month)
			else:
				month = str(next_date.month)
			if(next_date.day < 10):
				day = "0" + str(next_date.day)
			else:
				day = str(next_date.day)
			date_str = month + '/' + day + '/' + year
			self._set_day(date_str, sch)

class GetPlaylists:

	def GET(self):
		playlists = []
		playlist_keys = redis.keys('playlist:*')
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		print playlists
		return json.dumps(playlists)

class GetPlaylist:

	def GET(self):
		params = web.input()
		playlist = params.playlist
		plist = redis.get('playlist:' + playlist)
		return plist

class SetDefault:

	def POST(self):
		params = web.input()
		playlist = params.plist
		redis.set('defaultPlaylist', playlist)

class GetClips:

	def GET(self):
		cues = {}
		cue_keys = redis.keys('cue:*')
		for i in cue_keys:
			cueName = i.split(':')[1]
			cues[cueName] = redis.get(i)
		print cues
		return json.dumps(cues)

class ClearPlaylists:

	def GET(self):
		playlist_keys = redis.keys('playlist:*')
		for i in playlist_keys:
			redis.delete(i)

class ClearCues:

	def GET(self):
		cue_keys = redis.keys('cue:*')
		for i in cue_keys:
			redis.delete(i)

if __name__ == "__main__":
	pm = PlaylistManager()
	pm.setDaemon(True)
	pm.start()
	sm = ScheduleManager()
	sm.setDaemon(True)	
	sm.start()
	app = web.application(urls, globals())
	app.run()