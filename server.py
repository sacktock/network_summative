import socket
import sys
import json
import os
import time
from _thread import *
import threading

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
        if board_num < 0:
            raise IndexError
        path += boards[board_num] + '/'
        print('serving valid GET_MESSAGES request') 
    except IndexError:
        return b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "404 message board does not exist" }'
       
    files = [f.path for f in os.scandir(path) if f.is_file()]
    files = files[::-1]
    if len(files) > 100:
        files = files[:100]
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
        if board_num < 0:
            raise IndexError
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

def on_new_client(connection, client_address):
    try:
        print('connection from', client_address)
        raw_data = b''
        # Receive the data in small chunks and retransmit it

        path = './server.log'
        file = open(path, 'a+')
        file.write('connection from '+ str(client_address)+', ')
        file.write('on '+get_rich_timestamp()+', ')
        
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
        try:
            params = json.loads(raw_json)
        
            if params['request'] == 'GET_BOARDS':
                file.write('GET_BAORDS request ')
                response = GET_BOARDS()
            elif params['request'] == 'GET_MESSAGES':
                file.write('GET_MESSAGES request ')
                if ('board_num' in params) and isInt(params['board_num']):
                    response = GET_MESSAGES(params['board_num'])
                else:
                    response = b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "400 bad request"}'
            elif params['request'] == 'POST_MESSAGE':
                file.write('POST_MESSAGE request ')
                if ('board_num' in params) and isInt(params['board_num']) and ('title' in params) and ('content' in params):
                    response = POST_MESSAGE(params['board_num'], params['title'], params['content'])
                else:
                    response = b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "400 bad request"}'
            else:
                response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0, "error" : "400 bad request"}'
        except:
            response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0, "error" : "400 bad request"}'

        if b'error' in response:
            file.write('ERROR')
            print('error occured ... ')
        else:
            file.write('OK')
        file.write('\n')
        file.close()
        print('sending data back to the client')
        print(response)
        connection.sendall(response)
        
    finally:
        # Clean up the connection
        connection.close()
        
server_name = 'localhost'
port = 12000

args = sys.argv[1:]

# Parse commandline arguments
if (len(args) != 2):
    print ('server.py usage: python server.py <serverip> <port>')
    sys.exit(2)
else:
    server_name = str(args[0])
    port = int(args[1])

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port

server_address = (server_name, port)
print('starting up on {} port {}'.format(*server_address))
try:
    sock.bind(server_address)
except:
    print('error with socket '+str(server_address)+ ' ... unavailable/busy port ... ')
    sys.exit(2)

# checking if there are any message boards
path = './board/'
try:
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    if boards == []:
        print('error: no message boards ... ')
        sys.exit(2)
except:
    print('error: board folder not found ...')
    sys.exit(2)

    
# Listen for incoming connections
sock.listen(1)

response = b''

while True:
    # Wait for a connection
    print('waiting for a connection...')
    try:
        connection, client_address = sock.accept()
    except KeyboardInterrupt:
        print('\nkeyboard interrupt ... ')
        sys.exit(2)
    try:
        start_new_thread(on_new_client,(connection, client_address))
    except:
        print("couldn't create a new thread...")
        

sock.close()

