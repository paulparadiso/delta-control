import web
import redis

urls = (
	'/', 'index',
)

render = web.template.render('templates')
#print render.hello('world')

class index:

	def GET(self):
		header = render.header()
		nav = render.nav()
		return render.test(header, nav)

if __name__ == "__main__":	
	app = web.application(urls, globals())
	app.run()