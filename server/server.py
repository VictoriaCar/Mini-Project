import threading
import socket
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

    ref.set({
        'key0' : {
            'timestamp' : time.time(),
            'old_timestamp' : -1,
            'username' : 'user000',
            'content' : 'TEST MESSAGE 0',
            'old_content' : -1,
        },
        'key1' : {
            'timestamp' : time.time(),
            'old_timestamp' : -1,
            'username' : 'user001',
            'content' : 'TEST MESSAGE 1',
            'old_content' : -1,
        },
    })

    print(db.reference('/test/').get()) # should see key0 and key1

# update messages
def update_message(user, new_content):
    # for now we can directly assume the key is user000
        # user000Ref = usersRef.child('user000')
        # user000Ref.update({
        #     'o_timestamp' : time.time,
        #     'o_content' : 'TEST MESSAGE 1'
        # })

    # using push() we'll need a for loop - also using key
    ref = get_users()
    for k, v in ref.get().items():
        if v['username'] == user:
            old_timestamp = v['timestamp']
            old_content = [].extend(v['content'])

            ref.child(k).update({
                'timestamp' : time.time(),
                'old_timestamp' : old_timestamp,
                'content' : new_content,
                'old_content' : old_content,
            })

# delete
def delete_message(user, new_content):
    ref = get_users()
    for k, v in ref.get().items():
        if v['username'] == user:
            ref.child(k).set({})

# read
def read_messages(user):
    ref = get_users()
    for k, v in ref.get().items():
        if v['username'] == user:
            print(ref.get())
    

init_test()


# init socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

host = IPAddr
port = 7807

serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((host,port))
backlog = 256

serverSocket.listen()
size = 4096


# server
quit_server = False
print(host,port)
def server():
    global quit_server
    message_queue = [] # store all the .accept() threads in here, then process
    print("webserver live")
    while not quit_server:
        clientSocket, src = serverSocket.accept()
        ipaddr, port = src
        try:
            message = clientSocket.recv(size).decode()
            print("message from ["+ipaddr+"]:", message)
            if message == "QUIT":
                quit_server = True
                break
        except IOError:
            MESSAGE = "socket not connected"
            clientSocket.send(MESSAGE.encode())
            clientSocket.close()

    serverSocket.close()

        # wait for msg
        # recieve msg
        # parse msg
            # src - dest
            # info
            # content

        
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