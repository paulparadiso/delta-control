import settings
import socket
import time

ribbon_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ribbon_sock.bind(settings.addresses['ribbon'])
ribbon_sock.settimeout(0.1)
concierge_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
concierge_sock.bind(settings.addresses['concierge'])
ribbon_sock.settimeout(0.1)

def main():
	while(True):
		try:
			data, addr = ribbon_sock.recvfrom(10000)
			if data:
				print "Ribbon message - " + data
		except socket.timeout:
			pass
		try:
			data, addr = concierge_sock.recvfrom(10000)
			if data:
				print "Concierge message - " + data
		except socket.timeout:
			pass
		time.sleep(0.1)

if __name__ == '__main__':
	main()