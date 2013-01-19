commands = {
	'power_on': 'POWER_ON',
	'power_off': 'POWER_OFF',
	'cue': 'CUE',
	'play': 'PLAY',
	'pause': 'PAUSE',
	'stop': 'STOP',
	'skip': 'SKIP',
	'goto': "GOTOMARKER \"%s\" play",
	'wait': "%s_DONE",
}

addresses = {
	'self': 34450,
	'ribbon': ('127.0.0.1', 34448),
	'concierge': ('127.0.0.1', 34449)
}