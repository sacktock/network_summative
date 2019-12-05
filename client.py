import socket
import sys
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
                print('server responded badly ... ')
                print('exiting ... ')
                sys.exit()
            if response['valid'] == 1:
                return response
            
            elif response['valid'] == 0:
                print(response['error']+' error ... ')
                retry =input('Try again : [Y/N] ')
                print('exiting ... ')
                sys.exit()
            else:
                print('server responded badly ... ')
                print('exiting ... ')
                sys.exit()
                
        else:
            print('nothing received from the server ... ')
            print('exiting ... ')
            sys.exit()

def GET_MESSAGES(board_num):
    message = '{"request" : "GET_MESSAGES", "board_num" : '+ str(board_num) +'}'
    while True:
        response = server_request(message)
        if response:
            try:
                response = json.loads(response)
            except:
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
            
            if response['valid'] == 1:
                # parse data and display message board
                board_title = response['board']
                messages = response['messages'] # messages is a list of dicts
                print()
                print('Message Board :')
                print()
                print('==== '+ board_title+ ' ====')
                print()
                if messages == []:
                    print()
                    print('no messages ... ')
                    print()
                else:
                    for message in messages:
                        print('----------'+'-'*(len(board_title)))
                        print()
                        print(parse_title(message['title']))
                        print()
                        print(message['content'])
                        print()
                        print('----------'+'-'*(len(board_title)))
                print()
                print('=========='+'='*(len(board_title)))
                print()
                while True:
                    action = input('Return to message boards : R + [Enter] , Exit : QUIT + [Enter] ')
                    if action == 'R':
                        print('returning to message boards ... ')
                        break
                    elif action == 'QUIT':
                        print('exiting ... ')
                        sys.exit()
                break
                
            elif response['valid'] == 0:
                print(response['error']+' error ... ')
                print('returning to message boards ... ')
                break
            else:
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
        else:
            print('nothing received from the server ... ')
            print('returning to message boards ... ')
            break
    return 

def POST_MESSAGE(board_num, msg_title, msg_content):
    message = '{"request" : "POST_MESSAGE", "board_num" : '+ str(board_num) +' , "title" : "'+msg_title+'", "content" : "'+ msg_content+'"}'
    while True:
        response = server_request(message)
        if response:
            try:
                response = json.loads(response)
            except:
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break

            if response['valid'] == 1:
                print('message successfully posted ... ')
                break
    
            elif response['valid'] == 0:
                print(response['error']+' error ... ')
                print('returning to message boards ... ')
                break
            else:
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
        else:
            print('nothing received from the server ... ')
            print('returning to message boards ... ')
            break
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
        sock.close()
        print('server timeout ... ')
        print('exiting ... ')
        sys.exit()
        return b''
    except ConnectionRefusedError:
        sock.close()
        print('server is unavailable ... ')
        print('exiting ... ')
        sys.exit()
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
if (len(args) != 2):
    print ('client.py usage: python client.py <serverip> <port>')
    sys.exit(2)
else:
    server_name = str(args[0])
    port = int(args[1])
    
boards = GET_BOARDS()['boards']

# call GET_BOARDS to get the boards from the server
            
while True:
    print()
    print('==== Message Boards ====')
    print()
    if boards == []:
        print()
        print('no boards ... ')
        print()
    else:
        i = 0
        for board in boards:
            i += 1
            print(str(i)+'. '+board)
    print()
    print('========================')
    print()
    user_input = input('View message board : [number] + [Enter], Post a message : POST + [Enter], Exit : QUIT + [Enter] ')
    if user_input == 'POST':
        print('Posting a message requires : [board_number] [message_title] [message_content]')
        post_board = input('Enter [board_number] ... ')
        msg_title = input('Enter [message_title] ... ')
        msg_content = input('Enter [message_content] ... ')

        try:
            board_num = int(post_board)-1
            response = POST_MESSAGE(board_num, msg_title, msg_content)
        except ValueError:
            print('invalid boards number ... ')
        print('returning to message boards ... ')
            
    elif user_input == 'QUIT':
        print('exiting ... ')
        sys.exit()
    else:
        try:
            board_num = int(user_input) -1
            GET_MESSAGES(board_num)
        except ValueError:
            print('invalid board number ... ')
            print('returning to message boards ... ')
            


    
            



