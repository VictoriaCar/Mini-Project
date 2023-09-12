import os

#!/bin/bash

# device_ipv4=.keys/device_ipv4.pem
# AWS_SSH="ssh -i ~/.keys/ec2sshkey.pem ec2-user@3.130.58.56"

# os.system('./../.keys/scriptKey.sh')
os.system('pipreqs .')

os.system('scp -r -i ~/.keys/EC2WebServer.pem server/server.py ec2-user@ec2-3-130-58-56.us-east-2.compute.amazonaws.com:~/webserver/')
os.system('scp -r -i ~/.keys/EC2WebServer.pem server/Firebase.json ec2-user@ec2-3-130-58-56.us-east-2.compute.amazonaws.com:~/webserver/')
os.system('scp -r -i ~/.keys/EC2WebServer.pem requirements.txt ec2-user@ec2-3-130-58-56.us-east-2.compute.amazonaws.com:~/webserver/requirements.txt')

os.system('ssh -t -i ~/.keys/EC2WebServer.pem ec2-user@ec2-3-130-58-56.us-east-2.compute.amazonaws.com \'pip install -r ~/webserver/requirements.txt\'')
# os.system('ssh -t -i ~/.keys/EC2WebServer.pem ec2-user@ec2-3-130-58-56.us-east-2.compute.amazonaws.com \'python3 ~/webserver/server.py\'')
# this file scp the server.py script into AWS EC2