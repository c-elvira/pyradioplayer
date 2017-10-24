from __future__ import unicode_literals

# Python
import os
import sys
import time
import socket
import queue
import threading

from subprocess import call

# External library
import vlc
import youtube_dl

# My library
from homepyShell import AHomePyShell

# Remark : I use ffmeg on my raspberry pi
# echo "alias youtube-dl='youtube-dl --prefer-ffmpeg'" | tee -a ~/.bashrc; . ~/.bashrc
# According to
# https://askubuntu.com/questions/645462/avconv-version-and-youtube-dl

URL_FIP = "http://direct.fipradio.fr/live/fip-midfi.mp3"
ADDRESS = ''
PORT = 10000
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'
HOMEPY_SOCKET_TIME_OUT = 2.0


class ExceptionDoNotExist(Exception):
    """docstring for QuitException"""

    def __init__(self):
        super(ExceptionDoNotExist, self).__init__()


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

    def do_listen(self, arg):
        """
        Change Media. For instance
        listen youtube url
        """
        args = arg.split(' ')
        if len(args) == 2:
            if args[0].lower() == 'youtube':
                self.homepyServer.listenOneYoutubeVideo(args[1])
            else:
                print('Not implemented or unknown')
        else:
            print('wrong number of arguments')

    # Misc
    def setServer(self, HomePyServer):

        self.homepyServer = HomePyServer
        self.sock = None


class HomePyNetwork(object):

    def __init__(self, callbackEvent):
        super(HomePyNetwork, self).__init__()

        self.sock = None
        self.atomicBoolQuit = AtomicBool(False)
        self.callbackProcessEvent = callbackEvent

    def bindAddress(self):

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # The socket might raise an exception if the address has been
        # used recently.
        # This option tells the socket to reuse the adress
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        server_address = (ADDRESS, PORT)
        self.sock.bind(server_address)

    def serverloop(self):
        """
            Server
        """

        # Listen for incoming connections
        self.sock.listen(1)

        while not self.atomicBoolQuit.get():
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.sock.accept()

            try:
                print('connection from ' + str(client_address))

                while not self.atomicBoolQuit.get():
                    try:
                        connection.settimeout(HOMEPY_SOCKET_TIME_OUT)
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
                        self.callbackProcessEvent(recevied_message)

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

    def closeNetwork(self):
        self.atomicBoolQuit.set(True)


class HomePyMedia(object):
    """docstring for HomePyMedia"""

    def __init__(self, callbackRadioStop):
        super(HomePyMedia, self).__init__()

        self.vlc_instance = None
        self.vlc_player = None
        self.quit = AtomicBool(False)

        self.media_radio = None
        self.media_mp3 = None

        self.callbackRadioStop = callbackRadioStop

        self.lastmp3file = None
        self.lastRadio = None
        self._lock = threading.Lock()

        # Delete old temporary mp3 file
        for filename in os.listdir('.'):
            if filename.endswith('.mp3'):
                os.remove(filename)

    def _set_media(self, media):
        if not self.vlc_player.is_playing():
            self.vlc_player = self.vlc_instance.media_player_new()

        self.vlc_player.set_media(media)

    def callbackEndYoutube(self, event):

        # Sometimes, the callback is called twice...
        if self.lastmp3file is not None:
            self.listen_radio()

            with self._lock:
                os.remove(self.lastmp3file)
                self.lastmp3file = None
        else:
            raise Exception('callbackEndYoutube has been called twice....')

    def listen_radio(self, url_radio=None):

        if url_radio is None:
            self.media_radio = self.vlc_instance.media_new(self.lastRadio)

        else:
            self.media_radio = self.vlc_instance.media_new(url_radio)
            self.lastRadio = url_radio

        with self._lock:
            self._set_media(self.media_radio)
            self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.callbackRadioStop)
            self.vlc_player.play()

    def listen_oneYoutubeVideo(self, url_youtube):

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }]
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                dwnld_report = ydl.download([url_youtube])
            if dwnld_report:
                print('Can\'t download youtube video')
                return

            # Search for the file
            for filename in os.listdir('.'):
                if filename.endswith('.mp3'):
                    with self._lock:
                        self.lastmp3file = filename
                    break

            self.media_mp3 = self.vlc_instance.media_new(self.lastmp3file)
            self._set_media(self.media_mp3)
            self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.callbackEndYoutube)
            self.vlc_player.play()

        except youtube_dl.DownloadError as e:
            print(e)
            raise ExceptionDoNotExist


    def start(self):
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

    def play(self):
        if self.vlc_player is not None:
            self.vlc_player.play()

    def pause(self):
        if self.vlc_player is not None:
            self.vlc_player.pause()

    def set_volume(self, newVolume):
        if self.vlc_player is not None:
            self.vlc_player.audio_set_volume(int(newVolume))


class HomePyServer(object):
    """
        docstring for HomePyServer
    """

    def __init__(self):
        super(HomePyServer, self).__init__()

        self.moduleNetwork = None
        self.moduleMedia = None

        self.queueEvent = queue.Queue()
        self.thread_server = None

        self.atomicBoolQuit = AtomicBool(False)

    def __exit__(self):
        print('Byyyy :)')

    def callbackRadioStop(self, event):
        """
            Fonction
        """
        self.queueEvent.put('restart radio')

    def callbackProcessEvent(self, event):
        self.queueEvent.put(event)

    def start(self):

        print('HomePyServer has started\n')
        print('Initialize')

        try:
            # Creating module
            self.moduleNetwork = HomePyNetwork(self.callbackProcessEvent)
            self.moduleNetwork.bindAddress()

            # Threding stuff
            self.thread_server = threading.Thread(target=self.moduleNetwork.serverloop)
            self.thread_server.start()
            print('\tListening to event')

        except Exception as e:
            raise e

        try:
            self.moduleMedia = HomePyMedia(self.callbackRadioStop)
            self.moduleMedia.start()
            print('\tReady to stream music')

        except Exception as e:
            raise e

        self.whenStarted()

        self.mainloop()

    def mainloop(self):
        """
            An infinite loop than inspect a queue
        """

        shell = ServerHomePyShell()
        shell.setServer(self)

        while not self.atomicBoolQuit.get():
            try:
                event = self.queueEvent.get(True, None)
                shell.onecmd(event)

            except NotImplementedError:
                print('The command is not implemented yet')

            except ExceptionDoNotExist:
                print('Youtube said that the video does exist. Return to radio')

            except Exception as e:
                print('An exception has been catched')
                print(e)

        # The program is about to quit, wait for the thread
        print('Closing network...')
        self.moduleNetwork.closeNetwork()
        self.thread_server.join()
        print('done')

    def kill(self):
        self.atomicBoolQuit.set(True)

    def changeVolume(self, newvolume):
        self.moduleMedia.set_volume(newvolume)

    def play(self, bool_action):

        if self.moduleMedia is not None and not bool_action:
            self.moduleMedia.pause()

        elif self.moduleMedia is not None and bool_action:
            self.moduleMedia.play()

    def listenOneYoutubeVideo(self, url_video):
        self.moduleMedia.listen_oneYoutubeVideo(url_video)

    def whenStarted(self):

        print('By default, the french radio FIP is streamed')
        self.moduleMedia.listen_radio(URL_FIP)
        self.moduleMedia.set_volume(100)


if __name__ == '__main__':

    if sys.platform == "linux" or sys.platform == "linux2":
        # amixer cset numid=1 100%,100%
        call(["amixer", "cset", "numid=1", "100%,100%"])

    my_pyserver = HomePyServer()
    my_pyserver.start()

    print('by :)')
