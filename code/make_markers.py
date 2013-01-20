import redis

if __name__ == "__main__":
	r_s = redis.Redis()
	f = open('Delta markers.csv', 'r')
	lines = f.readlines()
	for l in lines:
		s = l.strip().split(',')
		r_s.set('cue:' + s[0], s[1] + ':' + s[2])