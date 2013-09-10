import web
import redis
import json
import socket
import settings
import time
from datetime import date, timedelta
from settings import commands, addresses
from playlist import PlaylistManager
from scheduler import ScheduleManager
from threading import Lock

time.sleep(10.0)
print "starting..."

#SndMsg socket for testing playlist manager.

snd_msg_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
snd_msg_host = '127.0.0.1'
snd_msg_port = settings.addresses['self']
rib_sock = settings.addresses['ribbon']
con_sock = settings.addresses['concierge']

#Dictionary to lookup up number of days in a month.

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
	'/help', 'Help',
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
	redis.save()

#master.html

class Index:

	def GET(self):
		header = render.header()
		nav = render.nav('master')
		playlist_keys = redis.keys('playlist:*')
		playlists = []
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		cue_keys = redis.keys("cue:*")
		cues = []
		for i in cue_keys:
			cues.append(i.split(':')[1])
		return render.master(header, nav, playlists, cues)

#scheduling.html

class Scheduling:

	def GET(self):
		header = render.header()
		nav = render.nav('scheduling')
		playlist_keys = redis.keys("playlist:*")
		playlists = []
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		return render.scheduling(header, nav, playlists)

#playlists.html

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
		for i in playlist_keys:
			playlist_name = i.split(':')[1]
			playlist = json.loads(redis.get(i))
			playlists[playlist_name] = playlist
		return render.playlists(header, nav, playlists, cues)

	#Receive new playlists and enter them into the database.

	def POST(self):
		params = web.input()
		plist_name = params.name;
		plist_name = plist_name.lstrip()
		plist_name = plist_name.rstrip()
		plist_str = params.playlist
		plist = plist_str.split(":")
		del plist[-1]
		redis.set('playlist:' + plist_name, json.dumps(plist))
		redis.save()

#clips.html

class Clips:

	def GET(self):
		header = render.header()
		nav = render.nav('clips')
		cue_keys = redis.keys("cue:*")
		cues = []
		for i in cue_keys:
			cues.append(i.split(':')[1])
		return render.clips(header, nav, cues)

	#Receive new clip names and enter them into the database.

	def POST(self):
		params = web.input()
		clipName = params.clipName
		ribbonCue = params.ribbonCue
		conciergeCue = params.conciergeCue
		redis.set("cue:" + clipName, ribbonCue + ':' + conciergeCue)
		redis.save()

#help.html

class Help:

	def GET(self):
		header = render.header()
		nav = render.nav('help')
		return render.help(header, nav)

#sndmsg.html.  A 'hidden' file for testing.

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
		snd_msg_sock.sendto(msg, settings.addresses['self'])

#Receive commands from the UI to be sent to either the playlist manager or the video
#server.

class Command:
	
	def POST(self):
		params = web.input()
		if params.cmdtype == 'playlist':
			self._start_playlist(params.cmd)
		if params.cmdtype == 'control':
			self._control_cmd(params.cmd)
		if params.cmdtype == 'clip':
			self._start_clip(params.cmd)
	
	#Start a new playlist.

	def _start_playlist(self, plist):
		play_cmd = 'start/' + plist + '/now'
		redis.set('playlist_cmd', play_cmd)

	#Create a temporary playlist and add the clip to it.

	def _start_clip(self, clip):
		print "creating tempory playlist and adding - " + clip
		plist = []
		plist.append(clip)
		redis.set('playlist:instantPlaylist', json.dumps(plist))
		self._start_playlist('instantPlaylist')


	#Send a command to the video server.

	def _control_cmd(self, cmd):	
		control_cmd = settings.commands[cmd]
		print "sending - " + control_cmd
		if cmd == "skip":
			#snd_msg_sock.sendto('cmd/' + control_cmd, settings.addresses['self'])
			#pm.set_message('cmd/' + control_cmd)
			redis.set('playlist_cmd', 'cmd/' + control_cmd)
			return
		if cmd == "power_on" or cmd == "power_off":
			snd_msg_sock.sendto(control_cmd, settings.addresses['crestron'])
			return
		snd_msg_sock.sendto(control_cmd, rib_sock)
		snd_msg_sock.sendto(control_cmd, con_sock)

#Manage scheduled items.

class Date:

	def POST(self):
		params = web.input()
		if params.action == 'get':
			return self._get_scheduled_items(params)
		if params.action == 'set':
			return self._set_scheduled_items(params)

	#Return all scheduled items.

	def _get_scheduled_items(self, params):
		date = params.date
		date_key = 'scheduledItem:' + date + ':*'
		scheduled_keys = redis.keys(date_key)
		scheduled_items = {}
		for i in scheduled_keys:
			print "s item" + i
			split_key = i.split(':')
			hour = split_key[2]
			minute = split_key[3]
			playlist = redis.get(i)
			scheduled_items[hour + ':' + minute] = playlist
		return json.dumps(scheduled_items)

	#Create a new scheduled item.

	def _set_scheduled_items(self, params):
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
			#self._clear_month(date)
			self._set_month(date, params)

	#Calculate the start date of a week.

	def _get_week_start(self, week, year):
		d = date(year, 1, 1) 	   
		delta_days = d.isoweekday() - 1
		delta_weeks = week
		if year == d.isocalendar()[0]:
			delta_weeks -= 1
		delta = timedelta(days=-delta_days, weeks=delta_weeks)
		return d + delta

	#Clear the scheduler for a particular day.

	def _clear_day(self, _date):
		#print "clearing " + _date
		keys = redis.keys('scheduledItem:' + _date + ':*')
		for i in keys:
			redis.delete(i)
		redis.save()

	#Clear a full week.

	def _clear_week(self, _date):
		date_lst = _date.split('/')
		#print "setting week of - " + _date
		week = date(int(date_lst[2]), int(date_lst[0]), int(date_lst[1])).isocalendar()[1]
		week_start = self._get_week_start(week, int(date_lst[2]))
		for i in range(0,5):
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

	#Clear a full month.

	def _clear_month(self, _date):
		date_lst = _date.split('/')
		for i in range(1, days_in_month[date_lst[0]] + 1):
			year = date_lst[2]
			month = date_lst[0]
			day = str(i + 1)
			new_date = month + '/' + day + '/' + year
			self._clear_day(new_date)

	#Set the scedule for a day.

	def _set_day(self, _date, sch):
		for key in sch.keys():
			if(key == "date" or key == "mode" or key == "action"):
				continue
			print "setting - " + _date
			redis.set("scheduledItem:" + _date + ":" + key, sch[key])
		redis.save()

	#Copy the a day's schedule to the entire month.

	def _set_month(self, _date, sch):
		date_lst = _date.split('/')
		#for i in range(1, days_in_month[date_lst[0]] + 1):
		#	year = date_lst[2]
		#	if(date_lst[0] < 10):
		#		month = "0" + date_lst[0]
		#	else:
		#		month = date_lst[0]
		#	if(i < 10):
		#		day = "0" + str(i)
		#	else:
		#		day = str(i)
		#	new_date = month + '/' + day + '/' + year
		#	self._set_day(new_date, sch)
		#current_day = int(date_lst[1])
		earliest_day = (int(date_lst[1]) - ((int(date_lst[1]) / 7) * 7))
		week = date(int(date_lst[2]), int(date_lst[0]), earliest_day).isocalendar()[1]
		week_start = self._get_week_start(week, int(date_lst[2]))
		b_staggered_months = False
		if week_start.month != int(date_lst[0]):
			b_staggered_months = True
		if b_staggered_months:
			year = str(week_start.year)
			if(week_start.day < 10):
				day = "0" + str(week_start.day)
			else:
				day = str(week_start.day)
			if(week_start.month < 10):
				month = "0" + str(week_start.month)
			else:
				month = str(week_start.month)
			week_to_set = month + '/' + day + '/' + year
			self._set_week(week_to_set, sch)
			week = date(int(date_lst[2]), int(date_lst[0]), earliest_day + 7).isocalendar()[1]
			week_start = self._get_week_start(week, int(date_lst[2]))
		current_day = week_start.day
		while  current_day < days_in_month[date_lst[0]]:
			year = date_lst[2]
			if(int(date_lst[0]) < 10):
				month = "0" + date_lst[0]
			else:
				month = date_lst[0]
			if(current_day < 10):
				day = "0" + str(current_day)
			else:
				day = str(current_day)
			new_date = month + '/' + day + '/' + year
			self._clear_week(new_date)
			self._set_week(new_date, sch)
			print "current day = " + str(current_day)
			current_day = current_day + 7


	#Copy a days schedule to the entire week.

	def _set_week(self, _date, sch):
		date_lst = _date.split('/')
		#print "setting week of - " + _date
		week = date(int(date_lst[2]), int(date_lst[0]), int(date_lst[1])).isocalendar()[1]
		week_start = self._get_week_start(week, int(date_lst[2]))
		for i in range(0,5):
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

	def POST(self):
		playlists = []
		playlist_keys = redis.keys('playlist:*')
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		print playlists
		return json.dumps(playlists)

#Get a particular playlist.

class GetPlaylist:

	def POST(self):
		params = web.input()
		playlist = params.playlist
		plist = redis.get('playlist:' + playlist)
		return plist


#Set the default playlist.


class SetDefault:

	def POST(self):
		params = web.input()
		playlist = params.plist
		print "setting " + playlist + " to default"
		redis.set('defaultPlaylist', playlist)
		redis.save()

#Get list of clips.

class GetClips:

	def POST(self):
		cues = {}
		cue_keys = redis.keys('cue:*')
		for i in cue_keys:
			cueName = i.split(':')[1]
			cues[cueName] = redis.get(i)
		#print cues
		return json.dumps(cues)

#Clear all playlists.

class ClearPlaylists:

	def GET(self):
		playlist_keys = redis.keys('playlist:*')
		for i in playlist_keys:
			redis.delete(i)
		redis.save()

#Clear all cues.

class ClearCues:

	def GET(self):
		cue_keys = redis.keys('cue:*')
		for i in cue_keys:
			redis.delete(i)
		redis.save()

def mutex_processor():
    mutex = Lock()

    def processor_func(handle):
        mutex.acquire()
        try:
            return handle()
        finally:
            mutex.release()
    return processor_func
		
if __name__ == "__main__":
	#sm = ScheduleManager()
	#sm.setDaemon(True)	
	#sm.start()
	pm = PlaylistManager()
	pm.setDaemon(True)
	pm.start()
	redis.set('playlist_cmd', 'None')
	app = web.application(urls, globals())
	app.add_processor(mutex_processor())
	app.run()