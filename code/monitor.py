import settings
import socket
import time

ribbon_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ribbon_sock.bind(settings.addresses['ribbon'])
ribbon_sock.settimeout(0.1)
concierge_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
concierge_sock.bind(settings.addresses['concierge'])
concierge_sock.settimeout(0.1)
out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
out_host = '127.0.0.1'
out_port = settings.addresses['self']
time_of_last_message = 0.0
message_wait_time = 20.0
done_template = "%s_DONE"
ribbon_done = ""
concierge_done = ""

def check_time():
	global ribbon_done
	global concierge_done
	global time_of_last_message
	global message_wait_time
	now = time.time()
	diff = now - time_of_last_message 
	if diff > message_wait_time:
		if ribbon_done != "":
			out_sock.sendto(ribbon_done,(out_host, out_port))
			ribbon_done = ""
		if concierge_done != "":
			out_sock.sendto(concierge_done,(out_host, out_port))
			concierge_done = ""

def main():
	global ribbon_done
	global concierge_done
	global time_of_last_message
	global message_wait_time
	while(True):
		try:
			data, addr = ribbon_sock.recvfrom(10000)
			if data:
				if 'GOTOMARKER' in data:
					ribbon_done = done_template % (data.split('"')[1])
					time_of_last_message = time.time()
					print "Ribbon message - %s" % (data)
				else:
					print "Ribbon Control Message <%s>" % (data)
		except socket.timeout:
			pass
		try:
			data, addr = concierge_sock.recvfrom(10000)
			if data:
				if 'GOTOMARKER' in data:
					concierge_done = done_template % (data.split('"')[1])
					time_of_last_message = time.time()
					print "Concierge message - %s" % (data)
				else:
					print "Concierge Control Message <%s>" % (data)
		except socket.timeout:
			pass
		check_time()
		#time.sleep(0.1)

if __name__ == '__main__':
	main()