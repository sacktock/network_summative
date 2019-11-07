import socket
import sys
import ipaddress
import json
import os
import time

def GET_BOARDS():
    print('serving valid GET_BOARDS request')
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    string = '['
    if boards != []:
        for board in boards:
            string += '"'+board+'", '
        string = string[:-2] + ']'
        return str.encode('{"request" : "GET_BOARDS", "valid" : 1, "boards" : '+string+'}')
    else:
        return b'{"request" : "GET_BOARDS", "valid" : 0, "error" : "404 no message boards found"}'

def GET_MESSAGES(board_num):
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    try:
        path += boards[board_num] + '/'
        print('serving valid GET_MESSAGES request') 
    except IndexError:
        return b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "404 message board does not exist" }'
       
    files = [f.path for f in os.scandir(path) if f.is_file()]
    messages = []
    
    for file in files:
        file = open(file, 'r')
        messages.append((os.path.basename(file.name),file.read()))
        file.close()

    string = '{"request" : "GET_MESSAGES", "valid" : 1, "board" : "'+boards[board_num]+'", "messages" : ['
    if messages != []:
        for message in messages:
            string += '{"title" : "'+ message[0] + '", "content" : "'+message[1]+'"}, '
        string = string[:-2]+']}'
        return str.encode(string)
    else:
        return str.encode('{"request" : "GET_MESSAGES", "valid" : 0, "error" : "404 no messages found"}')

def POST_MESSAGE(board_num, msg_title, msg_content):
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    try:
        path += boards[board_num] + '/'
    except IndexError:
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "404 message board does not exist" }'

    files = [f.name for f in os.scandir(path) if f.is_file()]
    msg_title = msg_title.rstrip()
    msg_title = msg_title.lstrip()
    msg_title = msg_title.replace(" ", "_")
    msg_title = get_timestamp()+'-'+msg_title
    if msg_title in files:
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "409 conflicting filename" }'
    
    try:
        file = open(path+msg_title,'w+')
        file.write(msg_content)
        file.close()
        return b'{"request" : "POST_MESSAGE", "valid" : 1}'
    except:
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "500 internal server failure" }'

def get_timestamp():
    t = time.gmtime()
    timestamp = str(t.tm_year)
    if t.tm_mon < 10:
        timestamp += '0'
    timestamp += str(t.tm_mon)
    if t.tm_mday < 10:
        timestamp += '0'
    timestamp += str(t.tm_mday)
    timestamp += '-'
    if t.tm_hour < 10:
        timestamp += '0'
    timestamp += str(t.tm_hour)
    if t.tm_min < 10:
        timestamp += '0'
    timestamp += str(t.tm_min)
    if t.tm_sec < 10:
        timestamp += '0'
    timestamp += str(t.tm_sec)
    return timestamp

def get_rich_timestamp():
    t = time.gmtime()
    return get_day(t.tm_wday)+' '+str(t.tm_mday)+' '+ get_month(t.tm_mon)+ ' '+str(t.tm_hour)+':'+str(t.tm_min)+':'+str(t.tm_sec)+' '+ str(t.tm_year) 
    
    
def get_month(month):
    switcher = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec',
    }
    return switcher.get(month, '')

def get_day(day):
    switcher = {
        0: 'Mon',
        1: 'Tue',
        2: 'Wed',
        3: 'Thu',
        4: 'Fri',
        5: 'Sat',
        6: 'Sun',
    }
    return switcher.get(day,'')

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

        path = './server.log'
        file = open(path, 'a+')
        file.write('\n')
        file.write('connection from '+ str(client_address)+'\n')
        file.write('on '+get_rich_timestamp()+'\n')
        
        while True:
            data = connection.recv(1024)
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
            file.write('GET_BAORDS request\n')
            response = GET_BOARDS()
        elif params['request'] == 'GET_MESSAGES':
            file.write('GET_MESSAGES request\n')
            if ('board_num' in params) and isInt(params['board_num']):
                response = GET_MESSAGES(params['board_num'])
            else:
                response = b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "400 bad request"}'
        elif params['request'] == 'POST_MESSAGE':
            file.write('POST_MESSAGE request\n')
            if ('board_num' in params) and isInt(params['board_num']) and ('title' in params) and ('content' in params):
                response = POST_MESSAGE(params['board_num'], params['title'], params['content'])
            else:
                response = b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "400 bad request"}'
        else:
            response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0, "error" : "400 bad request"}'

        if b'error' in response:
            file.write('ERROR : '+response.decode()+'\n')
            print('error occured ... ')
        else:
            file.write('OK : '+response.decode()+'\n')
        file.write('\n')
        file.close()
        print('sending data back to the client')
        print(response)
        connection.sendall(response)
        
    finally:
        # Clean up the connection
        connection.close()

