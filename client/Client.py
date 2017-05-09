"""Client program for CSE 310 Modified Tic Tac Toe Project

This program connects to a server and sends/receives commands to play the game.

The client program takes two inputs via command line
arguments: (i) the name of the machine on which the server program is running,
(ii) the port number that the server is listening at.
"""

import signal
import selectors
import sys
from socket import error as socket_error
import errno
from ClientClasses import TTTSocket, ClientState
from Input import parse_cmd, read_socket
import Commands

# Tell user if they did not provide enough arguments to the program
if len(sys.argv) < 3:
    print("Error: not enough arguments provided")
    print("Provide a servername and port")
    sys.exit()

# Check that port is a number
try:
    int(sys.argv[2])
except ValueError:
    print("Error: The 2nd argument (port) should be an integer.")
    sys.exit()

# Retrieve arguments
SERVER_NAME = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

# Client connection: INET, STREAMing socket
s = TTTSocket()

# Attempt to  Connect socket to server:
try:
    s.connect(SERVER_NAME, SERVER_PORT)
except socket_error as serr:
    if serr.errno == errno.ECONNREFUSED:
        print("Error: Connection Refused.")
        sys.exit()

# Signal handler for ctrl + C
def sigint_handler(signal, frame):
    Commands.exit(s, None)
    sys.exit(0)

# Install signal handler
signal.signal(signal.SIGINT, sigint_handler)

# Display connection information:
print("Now connected to " + SERVER_NAME + " on port " + str(SERVER_PORT))

# Create Client state object
state = ClientState()

# Initialize DefaultSelector for multiplexing STDIN and the socket
sel = selectors.DefaultSelector()
sel.register(s.s, selectors.EVENT_READ, read_socket)
sel.register(sys.stdin, selectors.EVENT_READ, parse_cmd)
while True: 
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(s, state)

