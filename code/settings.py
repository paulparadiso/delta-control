commands = {
	'power_on': 'POWER_ON',
	'power_off': 'POWER_OFF',
	'cue': 'CUE',
	'play': 'PLAY',
	'pause': 'STOP',
	'stop': 'GOTOMARKER \"BLACK\"',
	'skip': 'SKIP',
	'goto': "GOTOMARKER \"%s\" play\r",
	'wait': "%s_DONE",
}

addresses = {
	'self': ('127.0.0.1', 8920),
	'ribbon': ('127.0.0.1', 8921),
	'concierge': ('127.0.0.1', 8922),
	'crestron': ('127.0.0.1', 8923)
}