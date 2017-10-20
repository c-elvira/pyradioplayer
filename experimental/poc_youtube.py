from __future__ import unicode_literals
import youtube_dl

from time import sleep

import vlc

import os 


finish = 0

def SongFinished(event):
    global finish
    print("Event reports - finished")
    finish = 1





ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	dwnld_report = ydl.download(['https://www.youtube.com/watch?v=IVEaYIf68B0'])

if dwnld_report:
	error('Error during download')







for filename in os.listdir('.'):
	if filename.endswith('.mp3'):
		songfile = filename
		break





instance = vlc.Instance()

#Create a MediaPlayer with the default instance
player = instance.media_player_new()

#Load the media file
media = instance.media_new(songfile)

#Add the media to the player
player.set_media(media)

# attach event manager
events = player.event_manager()
events.event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)

#Play for 10 seconds then exit
bo = player.play()
if bo == -1:
	print('error while playing')

while finish == 0:
	sleep(0.2)
