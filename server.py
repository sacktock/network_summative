import socket
import sys
import ipaddress
import json
import os

def GET_BOARDS():
    print('serving valid GET_BOARDS request')
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    n = len(boards)
    string = '['
    for board in boards:
        string += '"'+board+'", '
    string = string[:-2] + ']'
    return str.encode('{"request" : "GET_BOARDS", "valid" : 1, "number" : '+str(n)+', "boards" : '+string+'}')

def GET_MESSAGES(board_num):
    # gather the file information and messages for the specified board number
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    try:
        path += boards[board_num] + '/'
        print('serving valid GET_MESSAGES request') 
    except IndexError:
        return b'{"request" : "GET_MESSAGES", "valid" : 0 }'
       
    files = [f.path for f in os.scandir(path) if f.is_file()]
    messages = []
    
    for file in files:
        file = open(file, 'r')
        messages.append((os.path.basename(file.name),file.read()))
        file.close()

    string = '{"request" : "GET_MESSAGES", "valid" : 1, "board" : "'+boards[board_num]+'", "messages" : ['
        
    for message in messages:
        string += '{"title" : "'+ message[0] + '", "content" : "'+message[1]+'"}, '
    string = string[:-2]+']}'
    return str.encode(string)

def POST_MESSAGE(board_num, msg_title, msg_content):
    # post the message in a file
    print('serving valid POST_MESSAGE request')
    return b'{"request" : "POST_MESSAGE", "valid" : 1}'

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
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

response = b''

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
        raw_json = raw_data.decode()
        params = json.loads(raw_json)
        
        if params['request'] == 'GET_BOARDS':
            response = GET_BOARDS()
        elif params['request'] == 'GET_MESSAGES':
            if ('board_num' in params) and isInt(params['board_num']):
                response = GET_MESSAGES(params['board_num'])
            else:
                response = b'{"request" : "GET_MESSAGES", "valid" : 0}'
        elif params['request'] == 'POST_MESSAGE':
            if ('board_num' in params) and isInt(params['board_num']) and ('title' in params) and ('content' in params):
                response = POST_MESSAGE(params['board_num'], params['title'], params['content'])
            else:
                response = b'{"request" : "POST_MESSAGE", "valid" : 0}'
        else:
            response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0}'
            
        print('sending data back to the client')
        connection.sendall(response)
    finally:
        # Clean up the connection
        connection.close()

