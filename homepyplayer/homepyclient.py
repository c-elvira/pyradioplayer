import socket
import sys

from homepyShell import AHomePyShell

try:

    if sys.argv[1] == 'test':
        ADDRESS = 'localhost'
    else:
        ADDRESS = '192.168.1.44'
except Exception as e:
    ADDRESS = '192.168.1.44'

PORT = 10000
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'


class QuitException(Exception):
    """docstring for QuitException"""

    def __init__(self):
        super(QuitException, self).__init__()


class SocketManager(object):
    """docstring for SocketManager"""

    def __init__(self):
        super(SocketManager, self).__init__()

        self.sock = None

    def __exit__(self):
        if self.sock is not None:
            self.sock.close()

    def start_connection(self):

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (ADDRESS, PORT)
        print('\tconnecting to ' + str(server_address))
        self.sock.connect(server_address)

    def send(self, msg):
        self.sock.sendall(msg.encode())

        # Look for the response
        amount_received = 0
        data_received = ''
        amount_expected = len(RESPONSE_SERVEUR)

        while amount_received < amount_expected:
            data = self.sock.recv(16)
            amount_received += len(data.decode())
            data_received += data.decode()

        return data_received


class ClientHomePyShell(AHomePyShell):

    connectionManager = None

    # ----- shell commands -----
    def do_quit(self, arg):
        'Close the HomePyServer as specified by the command line argument. Examples \n >>quit client'

        if arg == 'client':
            #return True
            raise QuitException
        elif arg == 'server':
            self.send('quit')
        else:
            print('Unknown argument for quit. Precise either \'client\' or \'server\'')

    def do_volume(self, arg):
        'Change the volume:  volume 20'

        if arg != '' and arg.isnumeric:
            self.send('volume ' + arg)

    def do_pause(self, arg=None):
        'pause the sound for an optional amount of time, in minute:  pause 60'

        # if arg.lower() == 'on' or arg.lower() == 'off':
        self.send('pause')
        # else:
        #     print('Unknown argument \'' + arg + '\' for pause. Precise either \'on\' or \'off\'')

    def do_play(self, arg=None):
        'play music again aften it has been stopped, in minute:  play'

        self.send('play')

    def do_listen(self, arg):
        """
        Change Media. For instance
        listen youtube url
        """
        args = arg.split(' ')
        if len(args) == 2:
            if args[0].lower() == 'youtube':
                self.send('listen ' + arg)
            else:
                print('Not implemented or unknown')
        else:
            print('wrong number of arguments')


    # Other Function
    def setConnectionManager(self, connectionManager):
        self.connectionManager = connectionManager

    def send(self, msg):
        if self.connectionManager is None:
            raise Exception('connection Manager is not set')

        print('sending ' + str(msg))
        msg += END_TRAME
        response = self.connectionManager.send(msg)

        if response != RESPONSE_SERVEUR:
            print('something really bad has happened')


if __name__ == '__main__':

    print('Waiting for a connection...')
    connectionManager = SocketManager()
    connectionManager.start_connection()
    print('...Connected!')

    shell = ClientHomePyShell()
    shell.setConnectionManager(connectionManager)
    shell.onecmd('help')
    while True:
        try:
            shell.cmdloop('')

        except QuitException:
            break

        except Exception as exception:
            print(exception)

        except NotImplementedError:
            print('The function you are calling is not implemented yet by the client')

    print('The homepyclient is about to quit. By')
