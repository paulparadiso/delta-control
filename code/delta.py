import web
import redis
import json

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
	'/clips','Clips',
	'/getclips','GetClips',
	'/clearplaylists', 'ClearPlaylists',
	'/clearcues', 'ClearCues',
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
		for i in playlist_keys:
			playlist_name = i.split(':')[1]
			playlist = json.loads(redis.get(i))
			playlists[playlist_name] = playlist
		return render.playlists(header, nav, playlists, cues)

	def POST(self):
		params = web.input()
		plist_name = params.name;
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
		editedClip = params.editedClip
		redis.delete('cue:' + editedClip);
		redis.set("cue:" + clipName, ribbonCue + ':' + conciergeCue)

class Command:
	
	def POST(self):
		#print d
		params = web.input()
		if params.cmdtype == 'playlist':
			self._start_playlist(params.cmd)
		if params.cmdtype == 'playback':
			self._control_cmd(params.cmd)
		if params.cmdtype == 'power':
			self._set_power(params.cmd)
			
	def _start_playlist(self, plist):
		print "starting playlist - " + plist
		
	def _control_cmd(self, cmd):
		print "sending playback command - " + cmd
		
	def _set_power(self, cmd):
		print "setting power to - " + cmd
		
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
		#print params.keys()
		date = params.date
		clear_date(date)
		for key in params.keys():
			if(key == "date"):
				continue
			redis.set("scheduledItem:" + date + ":" + key, params[key])


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
	app = web.application(urls, globals())
	app.run()