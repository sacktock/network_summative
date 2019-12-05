import socket
import sys
import json


# Client functions

def GET_BOARDS():
    # construct json message
    message = '{"request" : "GET_BOARDS"}'
    while True:
        # make server request
        response = server_request(message)
        if response:
            # parse json response
            try:
                response = json.loads(response.decode())
            except:
                # server doesn't respond with a json message
                print('server responded badly ... ')
                print('exiting ... ')
                sys.exit()
            if response['valid'] == 1:
                # valid response received
                return response
            elif response['valid'] == 0:
                # server side error
                print(response['error']+' error ... ')
                retry =input('Try again : [Y/N] ')
                print('exiting ... ')
                sys.exit()
            else:
                # server responded with unexpected json
                print('server responded badly no valid bit ... ')
                print('exiting ... ')
                sys.exit()
        else:
            # server didn't respond with anything
            print('nothing received from the server ... ')
            print('exiting ... ')
            sys.exit()

def GET_MESSAGES(board_num):
    # construct json message
    message = '{"request" : "GET_MESSAGES", "board_num" : '+ str(board_num) +'}'
    while True:
        # make server request
        response = server_request(message)
        if response:
            try:
                # parse json response
                response = json.loads(response.decode())
            except:
                # server doesn't respond with a json message
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
            
            if response['valid'] == 1:
                # valid response received
                # extract data and display messages
                board_title = response['board']
                messages = response['messages'] 
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
                    # wait for user input
                    action = input('Return to message boards : R + [Enter] , Exit : QUIT + [Enter] ')
                    if action == 'R':
                        print('returning to message boards ... ')
                        break
                    elif action == 'QUIT':
                        print('exiting ... ')
                        sys.exit()
                break
                
            elif response['valid'] == 0:
                # server side error
                print(response['error']+' error ... ')
                print('returning to message boards ... ')
                break
            else:
                # server responded with unexpected json
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
        else:
            # server didn't respond with anything
            print('nothing received from the server ... ')
            print('returning to message boards ... ')
            break
    return 

def POST_MESSAGE(board_num, msg_title, msg_content):
    # construct json message
    message = '{"request" : "POST_MESSAGE", "board_num" : '+ str(board_num) +' , "title" : "'+msg_title+'", "content" : "'+ msg_content+'"}'
    while True:
        # make server request
        response = server_request(message)
        if response:
            try:
                # parse json response
                response = json.loads(response.decode())
            except:
                # server doesn't respond with a json message
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
            if response['valid'] == 1:
                # valid response received
                print('message successfully posted ... ')
                break
            elif response['valid'] == 0:
                # server side error
                print(response['error']+' error ... ')
                print('returning to message boards ... ')
                break
            else:
                # server responded with unexpected json
                print('server responded badly ... ')
                print('returning to message boards ... ')
                break
        else:
            # server didn't respond with anything
            print('nothing received from the server ... ')
            print('returning to message boards ... ')
            break
    return 


def server_request(raw_json):
    # create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    #cConnect the socket to the port where the server is listening
    server_address = (server_name, port)
    print('connecting to {} port {}'.format(*server_address))
    try:
        sock.connect(server_address)
    except socket.timeout:
        # server timeout
        sock.close()
        print('server timeout ... ')
        print('exiting ... ')
        sys.exit()
        return b''
    except ConnectionRefusedError:
        # server is unavailable
        sock.close()
        print('server is unavailable ... ')
        print('exiting ... ')
        sys.exit()
        return b''
    
    response = b''
    
    try:
        # send message
        message = str.encode(raw_json)
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # look for the response
        while True:
            data = sock.recv(1024)
            print('received {!r}'.format(data))
            # construct the server response
            if data:
                response += data
            else:
                print('no more data from', server_address)
                break
            
    finally:
        # close the connection
        print('closing socket')
        sock.close()
        # return the server response
        return response


def parse_title(title):
    # converts the  given filename to a displayable title
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

# Main code
server_name = 'localhost'
port = 12000

args = sys.argv[1:]

# evaluate the commandline arguments
if (len(args) != 2):
    print ('client.py usage: python client.py <serverip> <port>')
    sys.exit(2)
else:
    server_name = str(args[0])
    port = int(args[1])

# call GET_BOARDS to get the boards from the server 
boards = GET_BOARDS()['boards']
           
while True:
    # display the message boards
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
    # wait for user input
    user_input = input('View message board : [number] + [Enter], Post a message : POST + [Enter], Exit : QUIT + [Enter] ')
    if user_input == 'POST':
        # start the POST_MESSAGE procedure
        print('Posting a message requires : [board_number] [message_title] [message_content]')
        # get user input
        post_board = input('Enter [board_number] ... ')
        msg_title = input('Enter [message_title] ... ')
        msg_content = input('Enter [message_content] ... ')

        # try parse the board number
        try:
            board_num = int(post_board)-1
            response = POST_MESSAGE(board_num, msg_title, msg_content)
        except ValueError:
            # user input is not a number
            print('invalid boards number ... ')
        print('returning to message boards ... ')
        
    elif user_input == 'QUIT':
        print('exiting ... ')
        sys.exit()
    else:
        # try parse the board number
        try:
            board_num = int(user_input) -1
            GET_MESSAGES(board_num)
        except ValueError:
            # user input is not a number
            print('invalid board number ... ')
            print('returning to message boards ... ')
            


    
            



