import socket

# Define the server's host and port
host = '3.130.58.56'  # Loopback address for local testing
port = 7807

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))

# Receive data from the server
emsg = "HELLO FROM LOCAL".encode()
data = client_socket.send(emsg)  # 4kb is the buffer size

# Close the client socket
client_socket.close()