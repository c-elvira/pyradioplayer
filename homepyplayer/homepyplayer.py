import vlc
import time

URL_FIP = "http://direct.fipradio.fr/live/fip-midfi.mp3"


bool_radio_stop = 0

class ExceptionRadioStop(Exception):
    pass

def RadioStop(event):
    raise('ExceptionRadioStop')

class HomePyPlayer(object):
	"""docstring for HomePyPlayer"""

	def __init__(self):
		super(HomePyPlayer, self).__init__()
		
		self.instance = vlc.Instance()
		self.player = self.instance.media_player_new()
		self.quit = False

	def start(self):

		print('HomePyPlayer has started\n')

		self.whenStarted()

		self.mainloop()


	def mainloop(self):
		
		while not self.quit:
			try:
				command = input(">> ")

				if command == 'exit':
					self.kill()
			except ExceptionRadioStop as exceptRadioStop:
				self.whenStarted



	def kill(self):
		print('Byy :)')
		self.quit = True

	def whenStarted(self):

		print('By default, the french radio FIP is streamed')
		self.media = self.instance.media_new(URL_FIP)
		self.player.set_media(self.media)
		self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, RadioStop)
		self.player.play()



my_player = HomePyPlayer()

my_player.start()