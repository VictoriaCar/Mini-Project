import json
import socket
import threading
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("webserver/Firebase.json")

firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://moodyapp-feec9-default-rtdb.firebaseio.com'
})

test_mode = True

# firebase
def get_users():
    global test_mode
    return db.reference('/users/') if test_mode else db.reference('/test/')

def init_test():
    # set data
    ref = db.reference("/")
    ref.set({
        "test" : -1
    })
    ref = db.reference('/test/')
    # ref.set({}) # delete first

    print(db.reference('/test/').get())

    # ref.push().set(value)
    # can use push() for autokey gen, leave as set() for test
    # ref = db.reference('/users/test/')
    '''
    organize the msg structure
    ID - email
        user
        msgs[(msg,timestamp)]
    '''

    ref.set({
       'key0' : {
            'email' : 'test@test.com',
            'username' : 'test',
            'messages' : [("hello world", time.time())],
       },
        'key1' : {
            'email' : 'test@test.com',
            'username' : 'test',
            'messages' : [("hello world", time.time())],
       },
    })

    # ref.set({
    #     'key0' : {
    #         'timestamp' : time.time(),
    #         'old_timestamp' : -1,
    #         'username' : 'user000',
    #         'content' : 'TEST MESSAGE 0',
    #         'old_content' : -1,
    #     },
    #     'key1' : {
    #         'timestamp' : time.time(),
    #         'old_timestamp' : -1,
    #         'username' : 'user001',
    #         'content' : 'TEST MESSAGE 1',
    #         'old_content' : -1,
    #     },
    # })

    print(db.reference('/test/').get()) # should see key0 and key1


def set_message(cmds):
    ref = get_users()
    for k, v in ref.get().items():
        if v['email'] == cmds['email']:
            ref.child(k).update({
                'messages' : [(cmds['message'],time.time())].extend(v['messages'])
            })
        return None
    
    ref.push({
        'email' : cmds['email'],
        'username' : cmds['username'],
        'messages' : [(cmds['message'], time.time())],
    })

# delete
def delete_message(cmds):
    ref = get_users()
    for k, v in ref.get().items():
        if v['email'] == cmds['email']:
            ref.child(k).set({})

# read
def get_message(cmds):
    ref = get_users()
    for k, v in ref.get().items():
        if v['email'] == cmds['email']:
            return ref.get()
    
    return None

# read
def read_messages(user):
    print(get_message(user))

# login
def user_login(cmds):
    ref = db.reference('/login')
    for k, v in ref.get().items():
        if v['email'] == cmds['email']:
            return v
    
def user_register(cmds):
    ref = db.reference('/login')
    ref.push({
         'email' : cmds['email'],
         'key' : cmds['key'],
     })


init_test()

def parse_command(packet):
    fbdb = {
        "GET" : get_message,
        "SET" : set_message,
        "DEL" : delete_message,
        "LOGIN" : user_login,
        "REGISTER" : user_register,
    }

    if packet['cmd'] not in fbdb.keys():
        return None
    else:
        return fbdb[packet['cmd']](packet)

# init socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

host = IPAddr
port = 7807

serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((host,port))
backlog = 256

serverSocket.listen(backlog)
size = 1024


# server
    # wait for msg - always wait for a msg
    # recieve & parse msg - THREAD TASK
        # src - dest
        # info
        # content


quit_server = False
def server():
    global quit_server
    global size
    message_queue = [] # store all the .accept() threads in here, then process
    print(f"Server is listening on {host}:{port}")
    while not quit_server:
        clientSocket, src = serverSocket.accept()
        ipaddr, port = src
        json_data = clientSocket.recv(size).decode()
        try:
            # CMD email username message
            # lex by 
            packet = json.loads(json_data)
            print("message from ["+ipaddr+"]:", packet)

            if packet['cmd'] == "QUIT":
                quit_server = True
                break

            data = parse_command(packet)
            if data['cmd'] == 'LOGIN':
                clientSocket.send(json.dumps(data).encode())
        except IOError:
            MESSAGE = "socket not connected"
            clientSocket.send(MESSAGE.encode())
            clientSocket.close()

    serverSocket.close()
        
def server_init():
    # we want to get the ip addr of the server
    # we want to create a task to recieve messagings
    # create a queue of messging (low volume traffic, no need for LB)
    threading.Thread(target=server).start()



if __name__ == "__main__":
    server_init()

### NOTES ###
    # to order by print order_by_child('field').get()
    # to sort by a param, do indexOn : ['field'] in Rule tab
    # this server handles client requests, multithreaded, and database handling
    # .join() preempts main until thread is done
    # use AWS CodeDeploy


    # sample deployment