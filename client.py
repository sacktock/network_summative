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
                print('Invalid response received from the server... ')
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
                for message in messages:
                    print('=======================')
                    print()
                    print(message['title'])
                    print()
                    print(message['content'])
                    print()
                    
                while True:
                    action = input('Return to message board : R + [Enter] , Exit : exit + [Enter] ')
                    if action == 'R':
                        break
                    elif action == 'exit':
                        sys.exit()
                break
                
            elif response['valid'] == 0:
                print('==== WARINING ====')
                print('Invalid response received from the server... ')
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
                print('Invalid response received from the server... ')
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

    # Connect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    try:
        sock.connect(server_address)
    except:
        return b''
    
    response = b''
    
    try:
        # Send data
        message = str.encode(raw_json)
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
    
board_num = 0
boards = GET_BOARDS()['boards']
n = len(boards)

# call GET_BOARDS to get the boards from the server
            
while True:
    print('==== Message Boards ====')
    for i in range(0,n):
        print(str(i+1)+'. '+boards[i])
    print('========================')
    user_input = input('View message board : [name] + [Enter], Post a message : post + [Enter], Exit : exit + [Enter] ')
    if user_input == 'post':
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
            
    elif user_input == 'exit':
        sys.exit()
    else:
        try:
            board_num = boards.index(user_input)
            GET_MESSAGES(board_num)
        except ValueError:
            print('==== WARINING ====')
            print('This board does not exist... ')
            print('==================')


    
            



