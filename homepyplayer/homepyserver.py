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

# My library
from homepyShell import AHomePyShell

URL_FIP = "http://direct.fipradio.fr/live/fip-midfi.mp3"
ADDRESS = ''
PORT = 10000
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'


class AtomicBool:
    """An atomic, thread-safe quit flag.

    """

    def __init__(self, initial=True):
        """
            Initialize a new atomic counter to given initial value (default 0).
        """
        self.value = initial
        self._lock = threading.Lock()

    def set(self, newvalue):
        """
            Atomically change the value of the boolean.
        """
        with self._lock:
            self.value = bool(newvalue)

    def get(self):
        with self._lock:
            return self.value


class ServerHomePyShell(AHomePyShell):

    homepyServer = None

    # ----- shell commands -----
    def do_quit(self, arg):
        """
            Close the HomePyServer as specified by the command line argument.
            Examples
            >>quit client
        """

        if self.homepyServer is not None:
            self.homepyServer.kill()

    def do_volume(self, arg):
        'Change the volume:  volume 20'

        self.homepyServer.changeVolume(int(arg))

    def do_pause(self, arg=None):
        'pause the sound for an optional amount of time, in minute:  pause 60'

        if self.homepyServer is not None:
            self.homepyServer.play(False)

    def do_play(self, arg=None):
        'play music again aften it has been stopped, in minute:  play'

        if self.homepyServer is not None:
            self.homepyServer.play(True)

    def do_restart(self, arg):

        if self.homepyServer is not None:
            if arg == 'radio':
                self.homepyServer.whenStarted()

    # Misc
    def setServer(self, HomePyServer):

        self.homepyServer = HomePyServer


class HomePyServer(object):
    """
        docstring for HomePyServer
    """

    def __init__(self):
        super(HomePyServer, self).__init__()

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.quit = AtomicBool(False)

        self.queueEvent = queue.Queue()
        self.thread_server = None

    def callbackRadioStop(self, event):
        """
            Fonction
        """
        self.queueEvent.put('restart radio')

    def start(self):

        print('HomePyServer has started\n')

        self.whenStarted()

        self.mainloop()

    def mainloop(self):
        """
            An infinite loop than inspect a queue
        """

        self.thread_server = threading.Thread(target=self.serverloop)
        self.thread_server.start()

        shell = ServerHomePyShell()
        shell.setServer(self)

        while not self.quit.get():
            try:
                event = self.queueEvent.get(True, None)
                shell.onecmd(event)

            except NotImplementedError:
                print('The command is not implemented yet')

        # The program is about to quit, wait for the thread
        self.killServer()
        self.thread_server.join()

    def serverloop(self):
        """
            Server
        """

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (ADDRESS, PORT)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while not self.quit.get():
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()

            try:
                print('connection from ' + str(client_address))

                while not self.quit.get():
                    try:
                        connection.settimeout(5.0)
                        recevied_message = ''
                        while True:
                            data = connection.recv(2048)
                            if data:
                                recevied_message += data.decode()
                            else:
                                break

                            if recevied_message.endswith(END_TRAME):
                                break
                            elif len(recevied_message) > 1000:
                                print('A cmd longer than 1000 character has been received')
                                break

                        connection.sendall(RESPONSE_SERVEUR.encode())
                        recevied_message = recevied_message.replace(END_TRAME, '')

                        print('received: ' + recevied_message)
                        self.queueEvent.put(recevied_message)

                    except socket.timeout as e:
                        err = e.args[0]
                        # this next if/else is a bit redundant, but illustrates
                        # how the timeout exception is setup
                        if err == 'timed out':
                            time.sleep(1)
                            continue
                        else:
                            print(e)

                    except socket.error as e:
                        # Something else happened, print error
                        # and handle it later
                        print(e)
                        break

                    except Exception as e:
                        # Something else happened, print error
                        # and handle it later
                        print(e)
                        break

            finally:
                # Clean up the connection
                connection.close()

    def kill(self):
        print('Byyyy :)')
        self.quit.set(True)

    def changeVolume(self, newvolume):

        self.player.audio_set_volume(int(newvolume))

    def play(self, bool_action):

        if self.player.is_playing() and not bool_action:
            self.player.pause()

        elif not self.player.is_playing() and bool_action:
            self.player.play()

    def killServer(self):

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

    my_pyserver = HomePyServer()
    my_pyserver.start()
