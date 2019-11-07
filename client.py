import socket
import sys
import ipaddress
import json


#######################################################################
############# CLIENT FUNCTIONS ########################################
#######################################################################

def GET_BOARDS():
    message = '{"request" : "GET_BOARDS"}'
    while True:
        response = server_request(message)
        if response:
            try:
                response = json.loads(response)
            except:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    sys.exit()
                else:
                    continue
            if response['valid'] == 1:
                
                return response
            
            elif response['valid'] == 0:
                print('==== WARINING ====')
                print(response['error']+' error - invalid response received from the server... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    sys.exit()
                else:
                    continue
            else:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    sys.exit()
                else:
                    continue
                
        else:
            print('==== WARINING ====')
            print('No response received from the server... ')
            print('==================')
            retry =input('Try again : [Y/N] ')
            if retry != 'Y':
                sys.exit()
            else:
                continue
    
    return 

def GET_MESSAGES(board_num):
    message = '{"request" : "GET_MESSAGES", "board_num" : '+ str(board_num) +'}'
    while True:
        response = server_request(message)
        if response:
            try:
                response = json.loads(response)
            except:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
            if response['valid'] == 1:
                # parse data and display message board
                board_title = response['board']
                messages = response['messages'] # messages is a list of dicts
                print('Message Board :')
                print('==== '+ board_title+ ' ====')
                print()
                if messages == []:
                    print()
                    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
                    print('////////////EMPTY MESSAGE BOARD\\\\\\\\\\\\\\\\')
                    print('///////////////////////////////////////////////')
                    print()
                else:
                    for message in messages:
                        print('=======================')
                        print()
                        print(parse_title(message['title']))
                        print()
                        print(message['content'])
                        print()
                    
                while True:
                    action = input('Return to message board : R + [Enter] , Exit : QUIT + [Enter] ')
                    if action == 'R':
                        break
                    elif action == 'QUIT':
                        sys.exit()
                break
                
            elif response['valid'] == 0:
                print('==== WARINING ====')
                print(response['error']+' error - invalid response received from the server... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
            else:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
        else:
            print('==== WARINING ====')
            print('No response received from the server... ')
            print('==================')
            retry =input('Try again : [Y/N] ')
            if retry != 'Y':
                break
            else:
                continue
    return 

def POST_MESSAGE(board_num, msg_title, msg_content):
    message = '{"request" : "POST_MESSAGE", "board_num" : '+ str(board_num) +' , "title" : "'+msg_title+'", "content" : "'+ msg_content+'"}'
    while True:
        response = server_request(message)
        if response:
            try:
                response = json.loads(response)
            except:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
            if response['valid'] == 1:
                print('Message successfully posted ... ')
                break
    
            elif response['valid'] == 0:
                print('==== WARINING ====')
                print(response['error']+' error - invalid response received from the server... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
            else:
                print('==== WARINING ====')
                print('Server responded badly... ')
                print('==================')
                retry =input('Try again : [Y/N] ')
                if retry != 'Y':
                    break
                else:
                    continue
        else:
            print('==== WARINING ====')
            print('No response received from the server... ')
            print('==================')
            retry =input('Try again : [Y/N] ')
            if retry != 'Y':
                break
            else:
                continue
    return 


def server_request(raw_json):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    # Connect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    try:
        sock.connect(server_address)
    except socket.timeout:
        print('Server timeout ... ')
        return b''
    except ConnectionRefusedError:
        print('Connection refused ... ')
        return b''
        
    
    response = b''
    
    try:
        # Send data
        message = str.encode(raw_json)
        print('sending {!r}'.format(message))
        sock.sendall(message)
        # start timer

        # Look for the response
        while True:
            # if > 10 seconds break
            data = sock.recv(1024)
            # reset timer
            print('received {!r}'.format(data))
            if data:
                response += data
            else:
                print('no more data from', server_address)
                break
            
    finally:
        print('closing socket')
        sock.close()
        return response


def parse_title(title):
    try:
        year = title[:4]
        month = str(int(title[4:6]))
        day = str(int(title[6:8]))
        hour = str(int(title[9:11]))
        mins = title[11:13]
        time = ''
        if int(hour) < 12:
            time = hour + '.'+mins+'am'
        else:
            time = str(int(hour)-12)+'.'+mins+'pm'
        text = title[16:]
        text = text.replace('_', ' ')
        return '"'+text+'" posted at '+time+' on '+day+' '+ get_month(int(month)) + ' '+year
    except:
        return ''
    
def get_month(month):
    switcher = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }
    return switcher.get(month, '')

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
    
boards = GET_BOARDS()['boards']

# call GET_BOARDS to get the boards from the server
            
while True:
    print('==== Message Boards ====')
    if boards == []:
        print()
        print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        print('///////////////NO BOARDS\\\\\\\\\\\\\\')
        print('//////////////////////////////////////')
        print()
    else:
        i = 0
        for board in boards:
            i += 1
            print(str(i)+'. '+board)
    print('========================')
    user_input = input('View message board : [name] + [Enter], Post a message : POST + [Enter], Exit : QUIT + [Enter] ')
    if user_input == 'POST':
        print('Posting a message requires : [board_name] [message_title] [message_content]')
        post_board = input('Enter [board_name] ... ')
        msg_title = input('Enter [message_title] ... ')
        msg_content = input('Enter [message_content] ... ')

        try:
            board_num = boards.index(post_board)
            response = POST_MESSAGE(board_num, msg_title, msg_content)
        except ValueError:
            print('==== WARINING ====')
            print('This board does not exist... ')
            print('==================')
            
    elif user_input == 'QUIT':
        sys.exit()
    else:
        try:
            board_num = boards.index(user_input)
            GET_MESSAGES(board_num)
        except ValueError:
            print('==== WARINING ====')
            print('This board does not exist... ')
            print('==================')


    
            



