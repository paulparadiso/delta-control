import redis

if __name__ == "__main__":
	r_s = redis.Redis()
	f = open('Delta markers.csv', 'r')
	lines = f.readlines()
	for l in lines:
		s = l.strip().split(',')
		for i in s:
			i = i.strip()
		print ('cue:%s=%s:%s:') % (s[0], s[1], s[2])
#		r_s.set('cue:' + s[0], s[1] + ':' + s[2])