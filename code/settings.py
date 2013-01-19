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
	'ribbon': ('10.0.90.101', 8920),
	'concierge': ('10.0.90.109', 8920),
	'crestron': ('10.0.90.21', 8920)
}