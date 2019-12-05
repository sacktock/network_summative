import socket
import sys
import json
import os
import time
from _thread import *
import threading

def GET_BOARDS():
    print('serving valid GET_BOARDS request')
    # scan the board folder for subfolders
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    string = '['
    if boards != []:
        # construct json response
        for board in boards:
            string += '"'+board+'", '
        string = string[:-2] + ']'
        return str.encode('{"request" : "GET_BOARDS", "valid" : 1, "boards" : '+string+'}')
    else:
        # no message boards
        return b'{"request" : "GET_BOARDS", "valid" : 0, "error" : "404 no message boards found"}'

def GET_MESSAGES(board_num):
    # scan the board folder for subfolders
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    # check if the board number is valid
    try:
        if board_num < 0:
            raise IndexError
        path += boards[board_num] + '/'
        print('serving valid GET_MESSAGES request') 
    except IndexError:
        # invalid board number
        return b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "404 message board does not exist" }'
    # scan the subfolder for files   
    files = [f.path for f in os.scandir(path) if f.is_file()]
    files = files[::-1]
    # get the most 100 recent messages
    if len(files) > 100:
        files = files[:100]
    # get the message content    
    messages = []
    for file in files:
        file = open(file, 'r')
        messages.append((os.path.basename(file.name),file.read()))
        file.close()
    # construct the json response
    string = '{"request" : "GET_MESSAGES", "valid" : 1, "board" : "'+boards[board_num]+'", "messages" : ['
    if messages != []:
        for message in messages:
            string += '{"title" : "'+ message[0] + '", "content" : "'+message[1]+'"}, '
        string = string[:-2]+']}'
        return str.encode(string)
    else:
        # no messages in the specified board
        return str.encode('{"request" : "GET_MESSAGES", "valid" : 0, "error" : "404 no messages found"}')

def POST_MESSAGE(board_num, msg_title, msg_content):
    # scan the board folder for subfolders
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    # check if the board number is valid
    try:
        if board_num < 0:
            raise IndexError
        path += boards[board_num] + '/'
    except IndexError:
        # invalid board number
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "404 message board does not exist" }'
    # scan the subfolder for files
    files = [f.name for f in os.scandir(path) if f.is_file()]
    # construct the filename
    msg_title = msg_title.rstrip()
    msg_title = msg_title.lstrip()
    msg_title = msg_title.replace(" ", "_")
    msg_title = get_timestamp()+'-'+msg_title
    if msg_title in files:
        # file already exists error
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "409 conflicting filename" }'
    try:
        # write to the file
        file = open(path+msg_title,'w+')
        file.write(msg_content)
        file.close()
        # return confirmation response
        return b'{"request" : "POST_MESSAGE", "valid" : 1}'
    except:
        # error occured return this response
        return b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "500 internal server failure" }'

def get_timestamp():
    # construct a timestamp for the filename
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

def on_new_client(connection, client_address):
    # server a client request
    try:
        print('connection from', client_address)
        raw_data = b''
        # open the .log file
        path = './server.log'
        file = open(path, 'a+')
        file.write('connection from '+ str(client_address)+'\t')
        file.write('on '+get_rich_timestamp()+'\t')

        # receive the data
        while True:
            data = connection.recv(1024)
            print('received {!r}'.format(data))
            # construct the request
            if data:
                raw_data += data
            if data.decode()[-1] =='}':
                print('end of data from', client_address)
                break
            
        # parse the response to a string
        raw_json = raw_data.decode()
            
        try:
            params = json.loads(raw_json)
        
            if params['request'] == 'GET_BOARDS':
                # write to .log file
                file.write('GET_BOARDS request\t')
                # serve a GET_BOARDS request
                response = GET_BOARDS()
            elif params['request'] == 'GET_MESSAGES':
                # write to .log file
                file.write('GET_MESSAGES request\t')
                # check the request is a valid GET_MESSAGES request
                if ('board_num' in params) and isInt(params['board_num']):
                    # serve a GET_MESSAGES request
                    response = GET_MESSAGES(params['board_num'])
                else:
                    # invalid request respond with error
                    response = b'{"request" : "GET_MESSAGES", "valid" : 0, "error" : "400 bad request"}'
            elif params['request'] == 'POST_MESSAGE':
                # write to .log file
                file.write('POST_MESSAGE request\t')
                # check the request is a valid POST_MESSAGE request
                if ('board_num' in params) and isInt(params['board_num']) and ('title' in params) and ('content' in params):
                    # server a POST_MESSAGE request
                    response = POST_MESSAGE(params['board_num'], params['title'], params['content'])
                else:
                    # invalid request respond with error
                    response = b'{"request" : "POST_MESSAGE", "valid" : 0, "error" : "400 bad request"}'
            else:
                # write to .log file
                file.write('UNKNOWN_REQUEST request\t')
                # unknown request respond with error
                response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0, "error" : "400 bad request"}'
        except:
            # write to .log file
            file.write('UNKNOWN_REQUEST request\t')
            # unknown request respond with error
            response = b'{"request" : "UNKNOWN_REQUEST", "valid" : 0, "error" : "400 bad request"}'

        # check if error has occured and write to .log file
        if b'error' in response:
            file.write('ERROR')
            print('error occured ... ')
        else:
            file.write('OK')
        file.write('\n')
        file.close()
        # close .log file
        # send response to the client
        print('sending data back to the client')
        print(response)
        connection.sendall(response)
    finally:
        # clean up the connection
        connection.close()
        
server_name = 'localhost'
port = 12000

args = sys.argv[1:]

# evaluate the commandline arguments
if (len(args) != 2):
    print ('server.py usage: python server.py <serverip> <port>')
    sys.exit(2)
else:
    server_name = str(args[0])
    port = int(args[1])

# create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the port

server_address = (server_name, port)
print('starting up on {} port {}'.format(*server_address))
try:
    sock.bind(server_address)
except:
    # socket unavailable/busy
    print('error with socket '+str(server_address)+ ' ... unavailable/busy port... ')
    sock.close()
    sys.exit(2)

# check if there are any message boards
try:
    # scan the board sub folder
    path = './board/'
    boards = [f.name for f in os.scandir(path) if f.is_dir()]
    if boards == []:
        # exit if no message boards
        print('error: no message boards ... ')
        sock.close()
        sys.exit(2)
except:
    # exit if no board folder
    print('error: board folder not found ...')
    sock.close()
    sys.exit(2)

    
# listen for incoming connections
sock.listen(1)

response = b''

while True:
    # wait for a connection
    print('waiting for a connection...')
    try:
        connection, client_address = sock.accept()
    except KeyboardInterrupt:
        print('\nkeyboard interrupt ... ')
        sock.close()
        sys.exit(2)
    try:
        # serve the client request on a new thread
        start_new_thread(on_new_client,(connection, client_address))
    except:
        # no threads left
        print("couldn't create a new thread...")
        sock.close()
        sys.exit(2)
        
sock.close()

