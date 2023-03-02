# socket_echo_server.py

from socket import socket
import sys

ADRESS = '0.0.0.0'
PORT = 4227

# Create a TCP/IP socket
sock = socket()

# Bind the socket to the port
server_address = (ADRESS, PORT)
sock.bind(server_address)
print(f'starting up on {ADRESS} port {PORT}')

# Listen for incoming connections
sock.listen()

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print(f'connection from {client_address}')

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(256)
            print(f'received {data}')
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print(f'no data from {client_address}')
                break

    finally:
        # Clean up the connection
        connection.close()


# socket_echo_client.py

# from socket import socket
# import sys

# ADRESS = 'localhost'
# PORT = 4227

# # Create a TCP/IP socket
# sock = socket()

# # Connect the socket to the port where the server is listening
# sock.connect((ADRESS, PORT))
# print(f'connected to {ADRESS} port {PORT}')

# try:
#     # Send data
#     message = b'This is the message.  It will be repeated.'
#     print(f'sending {message}')
#     sock.sendall(message)

#     # Look for the response
#     amount_received = 0
#     amount_expected = len(message)

#     while amount_received < amount_expected:
#         data = sock.recv(16)
#         amount_received += len(data)
#         print(f'received {data}')

# finally:
#     print('closing socket')
#     sock.close()