import socket
# import sys

ADRESS =  '192.168.1.44' # 'localhost'
PORT = 10000
RESPONSE_SERVEUR = 'OK'
END_TRAME = 'FINTRAME'

if __name__ == '__main__':

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (ADRESS, PORT)
    print('connecting to ' + str(server_address))
    sock.connect(server_address)

    while True:
        try:
            # Send data
            message = input('>>')

            if message == 'quit client':
                break

            print('sending ' + str(message) + ' ...')
            message += END_TRAME

            sock.sendall(message.encode())

            # Look for the response
            amount_received = 0
            data_received = ''
            amount_expected = len(RESPONSE_SERVEUR)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data.decode())
                data_received += data.decode()
                print(data_received)

            if data_received == RESPONSE_SERVEUR:
                print('everything goes well')
            else:
                print('something really bad has happened')
        except Exception as exception:
            print(exception)

    print('closing socket and client')
    sock.close()
