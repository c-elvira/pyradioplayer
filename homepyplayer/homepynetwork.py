import utils
import socket
import threading
import time

ADDRESS = ''
PORT = 10000
HOMEPY_SOCKET_TIME_OUT = 2.0
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'
MAX_CONNECTION = 20

class HomePyNetwork(object):

    def __init__(self, callbackEvent):
        super(HomePyNetwork, self).__init__()

        # The socket
        self.sock = None
        # use it 
        self._atomicBoolQuit = utils.AtomicBool(False)
        self.callbackProcessEvent = callbackEvent

        self.listSocketClient = []

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
        self.sock.settimeout(0.2)
        self.sock.listen(1)

        while not self._atomicBoolQuit.get():
            # Wait for a connection

            try:
                connection, client_address = self.sock.accept()

                newthread = ClientThread(client_address, connection, self.callbackProcessEvent)
                newthread.start()

            except socket.timeout:
                pass
            
            except:
                print(exception)
                raise
            else:
                self.listSocketClient.append(newthread)

            self.listSocketClient = [t for t in self.listSocketClient if t.is_alive()]
            thread_to_kill = [t for t in self.listSocketClient if not t.is_alive()]

            for t in thread_to_kill:
                print('before join')
                t.join()
                print('thread t has joined in loop')

        # Then kill all socket thread
        print('End loop')
        for t in self.listSocketClient:
            t.quit()
            print('thread t has quit')
            t.join()
            print('thread t has joined')

    def closeNetwork(self):
        self._atomicBoolQuit.set(True)







class ClientThread(threading.Thread):
    """
        Client connecting to the homepyserver.
        One instance per connexion.
    """
    
    def __init__(self, client_adress, clientsocket, callbackEvent):

        threading.Thread.__init__(self)
        self.ip = client_adress[0]
        self.port = client_adress[1]
        self.clientsocket = clientsocket
        self.callbackProcessEvent = callbackEvent
        self.atomicBoolQuitSocket = utils.AtomicBool(False)
        self.isRunning = utils.AtomicBool(False)

        print("[+] New thread for %s %s" % (self.ip, self.port, ))

    def run(self): 
   
        self.isRunning.set(True)
        print(" Listening " + str(self.ip) + ':' + str(self.port))

        try:
            while not self.atomicBoolQuitSocket.get():
                try:
                    self.clientsocket.settimeout(HOMEPY_SOCKET_TIME_OUT)
                    recevied_message = ''
                    while True:
                        data = self.clientsocket.recv(2048)
                        if data:
                            recevied_message += data.decode()
                        else:
                            break

                        if recevied_message.endswith(END_TRAME):
                            break
                        elif len(recevied_message) > 1000:
                            print('A cmd longer than 1000 character has been received')
                        break

                    self.clientsocket.sendall(RESPONSE_SERVEUR.encode())
                    recevied_message = recevied_message.replace(END_TRAME, '')

                    print('received: ' + recevied_message)
                    self.callbackProcessEvent(recevied_message)

                except socket.timeout as e:
                    err = e.args[0]
                    # this next if/else is a bit redundant, but illustrates
                    # how the timeout exception is setup
                    if err == 'timed out':
                        time.sleep(0.25)
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
            self.clientsocket.close()

        self.isRunning.set(False)
        print(str(self.ip) + ':' + str(self.port) + ' has deconnected')

    def quit(self):
        self.atomicBoolQuitSocket.set(True)