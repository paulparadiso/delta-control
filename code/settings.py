commands = {
	'power_on': 'POWER_ON\r',
	'power_off': 'POWER_OFF\r',
	'cue': 'CUE\r',
	'play': 'PLAY\r',
	'pause': 'STOP\r',
	'stop': 'GOTOMARKER BLACK\r',
	'skip': 'SKIP',
	'goto': "GOTOMARKER \"%s\" play\r",
	'wait': "%s_DONE",
	'startup': "SYSTEM_ON",
}
"""
Local settings
"""

addresses = {
	'self': ('127.0.0.1', 8920),
	'ribbon': ('127.0.0.1', 8921),
	'concierge': ('127.0.0.1', 8922),
	'crestron': ('127.0.0.1', 8923)
}

"""
Production settings
self = 10.0.90.20
"""

#addresses = {
#	'self': ('10.0.90.20', 8920),
#	'ribbon': ('10.0.90.101', 8920),
#	'concierge': ('10.0.90.109', 8920),
#	'crestron': ('10.0.90.21', 8920)
#}