import web
import redis
import json

urls = (
	'/', 'Index',
	'/master', 'Index',
	'/control','Command',
	'/playlists','Playlists',
	'/scheduling','Scheduling',
)

redis = redis.Redis('localhost')

render = web.template.render('templates')
#print render.hello('world')

class Index:

	def GET(self):
		header = render.header()
		nav = render.nav()
		playlist_keys = redis.keys('playlist:*')
		#playlists = ['test1','test2','test3','test4','test5']
		playlists = []
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		return render.master(header, nav, playlists)

class Scheduling:

	def GET(self):
		header = render.header()
		nav = render.nav()
		return render.scheduling(header, nav)

class Playlists:

	def GET(self):
		header = render.header()
		nav = render.nav()
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
		
if __name__ == "__main__":	
	app = web.application(urls, globals())
	app.run()