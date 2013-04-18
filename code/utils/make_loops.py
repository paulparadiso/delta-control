from optparse import OptionParser
import redis
import json
from datetime import datetime

class DeltaObject:

	def __init__(self, seed):
		#args = seed.split(':')
		self.type = ''
		self.name = ''
		self.items = []
		self.redis = redis.Redis()
		#if(len(args) > 0):
		#	self.type = args[0].strip().lower()
		#if(len(args) > 1):
		#	self.name = args[1].strip()
		if '%P%' in seed:
			self.type = 'playlist'
			seed = seed.strip('%P%').strip()
			self.name = seed
			return
		if '%S%' in seed:
			self.type = 'schedule'
			seed = seed.strip('%S%').strip()
			self.name = seed
			return
		if '%M%' in seed:
			self.type = 'marker'
			seed = seed.strip('%M%').strip()
			self.name = seed
			print "new item " + self.name
			return
		if '%D%' in seed:
			seed = seed.strip('%D%').strip()
			self.redis.set('defaultPlaylist', seed)
			print "defaultPlaylist = " + seed
			return

	def add_item(self, i):
		i = i.strip()
		if len(i) > 0:	
			self.items.append(i.strip())

	def save(self):
		if self.type == 'marker':
			#print "marker: " + self.name
			self._save_marker(self.name, self.items)
			#for i in self.items:
			#	print "\t%s" % (i)
		if self.type == 'schedule':
			#print "schedule for %s" % (self.name)
			for i in self.items:
				self._save_schedule(self.name, i)
			#	print "\t%s" % (i)
		if self.type == 'playlist':
			#print "playlist: " + self.name
			self._save_playlist(self.name, self.items)
			##for i in self.items:
			#	print "\t%s" % (i)

	def _save_marker(self, name, items):
		marker_str = items[0] + ':' + items[1]
		#print "marker - %s - %s" % (name, marker_str)
		self.redis.set('cue:' + name, marker_str)

	def _save_schedule(self, date, item):
		time_and_plist = item.split('-')
		if len(time_and_plist) > 1:
			time = time_and_plist[0].strip()
			plist = time_and_plist[1].strip()
		else:
			print "Incorrectly formatted schedule - %s" % (schedule)
			return
		pm = False
		if 'pm' in time:
			pm = True
			time = time.strip('pm').strip()
		if 'am' in time:
			pm = False
			time = time.strip('am').strip()
		hours_and_minutes = time.split(':')
		hours = int(hours_and_minutes[0].strip())
		if len(hours_and_minutes) > 1:
			minutes = (hours_and_minutes[1].strip())
			if len(minutes) < 2:
				minutes = '0' + minutes
		else:
			minutes = '00'
		if pm:
			hours = hours + 12
		if hours < 10:
			hours_str = '0' + str(hours)
		else:
			hours_str = str(hours)
		#date = date.replace('/',':')
		sched_str = 'scheduledItem:' + date + ':' + hours_str + ':' + minutes
		#print sched_str
		self.redis.set(sched_str, plist)

	def _save_playlist(self, name, items):
		self.redis.set('playlist:' + name, json.dumps(items))


class DeltaObjectBuilder:

	def __init__(self):
		self.current_object = None
		self.have_object = False

	def entry(self, e):
		if '%' in e:
			self._add_object(e)
		else:
			self._add_item(e)

	def _add_object(self, o):
		if self.have_object:
			#print "Saving Object."
			self.current_object.save()
			#print "Creating Object."
			self.current_object = DeltaObject(o)
		else:
			print "Creating Object."
			self.current_object = DeltaObject(o)
			self.have_object = True

	def _add_item(self, i):
		if self.have_object:
			self.current_object.add_item(i)
		else:
			print "Error - no object to add to."

	def save(self):
		if self.have_object:
			self.current_object.save()

def clean_entries(l):
	for i in range(len(l)):
		l[i] = l[i].rstrip()
	for i in l:
		#if i == '':
		#	l.remove(i)
		i = i.strip()
		if len(i) == 0:
			l.remove(i)

def process_file(f):
	ob = DeltaObjectBuilder()
	lines = f.readlines()
	clean_entries(lines)
	for i in lines:
		#print "adding line - " + i
		ob.entry(i)
	ob.save()

def main():
	parser = OptionParser()
	parser.add_option("-f", "--file", dest='filename',
					  help="Import loops file.", metavar="FILE")
	(options, args) = parser.parse_args()
	if options.filename == None:
		print "No input file specified."
		return
	try:
		f = open(options.filename, 'r')
		process_file(f)
	except IOError:
		print "Cannot find file %s" % (options.filename)
		return

if __name__ == "__main__":
	main()