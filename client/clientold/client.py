"""Client program for CSE 310 Modified Tic Tac Toe Project

This program connects to a server and sends/receives commands to play the game.

The client program takes two inputs via command line
arguments: (i) the name of the machine on which the server program is running, (ii) the port number
that the server is listening at. 
"""

from socket import socket, AF_INET, SOCK_STREAM
import sys
from part1 import game_help, game_login, game_exit, game_place, search_for_game

# Parse arguments
SERVER_NAME = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

# Client connection: INET, STREAMing socket
s = socket(AF_INET, SOCK_STREAM)
# Connect socket to server:
s.connect((SERVER_NAME,SERVER_PORT))

# Display information for user:
print("Now connected to " + SERVER_NAME + " on port " + str(SERVER_PORT))

# Prompt
prompt = "guest>"
# Login status
login_status = False

# Parse user commands
while True:
    # non blocking socket: check if EXIT
    cmd = input(prompt)
    if cmd == "help":
        game_help()
    elif cmd.split()[0] == "login":
        name = cmd.split()[1]
        login_status = game_login(s, name)
        if login_status:
            prompt = name + ">"
            search_for_game(s)
    elif cmd.split()[0] == "place":
        game_place(s, cmd.split()[1])
    elif cmd == "exit":
        game_exit(s)




