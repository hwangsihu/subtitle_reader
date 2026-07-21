from .pybass import *

sound = None

def init():
	return BASS_Init(-1, -1, 0, 0, 0)

def play(filename=None):
	global sound
	if sound:
		BASS_StreamFree(sound)
		sound = None
	
	if not filename:
		return
	
	if filename.find('http') == 0:
		sound = BASS_StreamCreateURL(filename.encode('utf-8'), 0, BASS_STREAM_AUTOFREE, None, None)
	else:
		sound = BASS_StreamCreateFile(False, filename.encode('utf-8'), 0, 0, BASS_STREAM_AUTOFREE)
	
	BASS_ChannelPlay(sound, True)

def free():
	BASS_Free()
