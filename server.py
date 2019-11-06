import socket
import sys
import ipaddress

server_name = 'localhost'
port = 12000

args = sys.argv[1:]

# Parse commandline arguments
if (len(args) == 2):
    server_name = args[0]
    try:
        ipaddress.ip_address(server_name)
        port = int(args[1])
        if not (1 <= port <= 65535):
            raise ValueError
    except:
        print ('server.py <serverip> <port>')
        sys.exit(2)
else:
    print('no arguments given using default socket')

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port

server_address = (server_name, port)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        raw_data = b''
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                raw_data += data
            if data.decode()[-1] =='}':
                print('end of data from', client_address)
                break
        # process the raw_data
        print('sending data back to the client')
        connection.sendall(raw_data)
    finally:
        # Clean up the connection
        connection.close()
