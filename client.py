import socket
import sys
import ipaddress

#######################################################################
############# CLIENT FUNCTIONS ########################################
#######################################################################

def GET_BOARDS():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    response = b''

    try:

        # Send data
        message = str.encode('{"request" : "GET_BOARDS"}')
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        while True:
            data = sock.recv(16)
            print('received {!r}'.format(data))
            if data:
                response += data
            else:
                print('no more data from', server_address)
                break
            
        print('data received from server: ',response)
    finally:
        print('closing socket')
        sock.close()
        return response

def GET_MESSAGES(board_num):
        # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    response = b''
    
    try:

        # Send data
        message = str.encode('{"request" : "GET_MESSAGES", "board_num" : '+ str(board_num) +'}')
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        while True:
            data = sock.recv(16)
            print('received {!r}'.format(data))
            if data:
                response += data
            else:
                print('no more data from', server_address)
                break
            
        print('data received from server: ',response)
    finally:
        print('closing socket')
        sock.close()
        return response

def POST_MESSAGE(board_num, msg_title, msg_content):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    
    response = b''
    
    try:

        # Send data
        message = str.encode('{"request" : "POST_MESSAGE", "board_num" : '+ str(board_num) +' , "title" : "'+msg_title+'", "content" : "'+ msg_content+'"}')
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        while True:
            data = sock.recv(16)
            print('received {!r}'.format(data))
            if data:
                response += data
            else:
                print('no more data from', server_address)
                break
            
        print('data received from server: ',response)
    finally:
        print('closing socket')
        sock.close()
        return response

#######################################################################
################## MAIN CODE ##########################################
#######################################################################

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
        print ('client.py <serverip> <port>')
        sys.exit(2)
else:
    print('no arguments given using default socket')

GET_BOARDS()
