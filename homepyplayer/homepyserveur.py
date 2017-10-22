from __future__ import unicode_literals

# Python
# import os
import sys
import time
import socket
import queue
import threading

from subprocess import call

# External library
import vlc
# import youtube_dl

URL_FIP = "http://direct.fipradio.fr/live/fip-midfi.mp3"
ADDRESS = ''
PORT = 10000
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'


class HomePyServeur(object):
    """
        docstring for HomePyServeur
    """

    def __init__(self):
        super(HomePyServeur, self).__init__()

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.quit = False

        self.queueEvent = queue.Queue()
        self.thread_serveur = None

    def callbackRadioStop(self, event):
        """
            Fonction
        """
        self.queueEvent.put('start lastradio')

    def start(self):

        print('HomePyServeur has started\n')

        self.whenStarted()

        self.mainloop()

    def mainloop(self):
        """
            An infinite loop than inspect a queue
        """

        self.thread_serveur = threading.Thread(target=self.serveurloop)
        self.thread_serveur.start()

        while not self.quit:
            if not self.queueEvent.empty():
                # Infinetely wait for something in the queue
                event = self.queueEvent.get(True, None)

                # For now, event is a string
                if event == 'quit' or event == 'exit':
                    self.kill()

                elif event == 'start lastradio':
                    self.whenStarted()

                else:
                    print('Unknown command')
            else:
                time.sleep(0.2)

        # The program is about to quit, wait for the thread
        self.killServeur()
        self.thread_serveur.join()

    def serveurloop(self):
        """
            Serveur
        """

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (ADDRESS, PORT)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while not self.quit:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()

            try:
                print('connection from ' + str(client_address))

                # Receive the data in small chunks and retransmit it
                recevied_message = ''
                while True:
                    data = connection.recv(512)
                    if data:
                        recevied_message += data.decode()
                        print(recevied_message)
                    else:
                        break

                    if recevied_message.endswith(END_TRAME):
                        break

                connection.sendall(RESPONSE_SERVEUR.encode())
                recevied_message = recevied_message.replace(END_TRAME, '')

                print('process : ' + recevied_message)
                self.queueEvent.put(recevied_message)

            finally:
                # Clean up the connection
                connection.close()

    def kill(self):
        print('Byyyy :)')
        self.quit = True

    def killServeur(self):

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 10000)
            sock.connect(server_address)

            message = 'kill'
            sock.sendall(message.encode())

        finally:
            sock.close()

    def whenStarted(self):

        print('By default, the french radio FIP is streamed')
        self.media = self.instance.media_new(URL_FIP)
        self.player.set_media(self.media)
        self.player.audio_set_volume(100)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.callbackRadioStop)
        self.player.play()


if __name__ == '__main__':

    if sys.platform == "linux" or sys.platform == "linux2":
        # amixer cset numid=1 100%,100%
        call(["amixer", "cset", "numid=1", "100%,100%"])

    my_pyserveur = HomePyServeur()
    my_pyserveur.start()
