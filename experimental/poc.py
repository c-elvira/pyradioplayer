import vlc
import time

URL_FIP = "http://direct.fipradio.fr/live/fip-midfi.mp3"

instance = vlc.Instance()

#Create a MediaPlayer with the default instance
player = instance.media_player_new()

#Load the media file
media = instance.media_new(URL_FIP)

#Add the media to the player
player.set_media(media)

#Play for 10 seconds then exit
player.play()
while True:
  pass