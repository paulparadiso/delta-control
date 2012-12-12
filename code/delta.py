import web
import redis

urls = (
	'/', 'index',
)

redis = redis.Redis('localhost')

render = web.template.render('templates')
#print render.hello('world')

class index:

	def GET(self):
		header = render.header()
		nav = render.nav()
		playlist_keys = redis.keys('playlist:*')
		playlists = ['test1','test2','test3','test4','test5']
		for i in playlist_keys:
			playlists.append(i.split(':')[1])
		return render.master(header, nav, playlists)
		
class control:
	
	def GET(self):
		print "play"

if __name__ == "__main__":	
	app = web.application(urls, globals())
	app.run()