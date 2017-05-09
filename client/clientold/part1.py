''' Functions to support commands required for part 1
'''
import sys
from socket import socket
from gamestate import display_game_state, finish_game, place_error
from helpers import exit_error, send_msg, get_messages, quit_received
from const import *


def game_help():
    ''' This command takes no argument. It prints a list of supported commands, which are ones in
    this list. For each command, it prints a brief description of the command function and
    the syntax of usage
    '''
    print("Supported commands:")
    print("help : Print a list of supported commands")
    print("login [name] : Login to the game server. Takes 1 argument, [name]")
    print("place [n] : Issues a move. Takes one argument [n], which is between 1 and 9 inclusive")
    print("exit : Exit the server")


def game_login(s, name):
    ''' This command takes one argument, your name. A player name is a userid that uniquely
    identifies a player. Your name is entered with this command and is sent to the server.
    Return True if login success, False if login failed.'''
    # Send message to server
    send_msg(s, LOGIN(name))

    # Receive response message from server
    response = s.recv(1024).decode()

    # Check response from server
    if response == OK:
        print("Logged in as " + name)
        return True
    elif response == ERR401:
        print("Login Failed. Try another name.")
        return False
    else:
        # Message from server is not recognized, close connection and exit
        exit_error(s, response)


def game_place(s, n):
    '''This command issues a move. It takes one argument n, which is between 1 and 9 inclusive.
    It identify a cell that the player chooses to occupy at this move. 
    If all is well, the new game state is received from the server and displayed.'''
    # Send place message to server
    send_msg(s, PLACE(n))

    # Receive response message from server
    responses = get_messages(s)
    if quit_received(responses):
        handle_exit(s)
    response = responses[0]

    if response.split()[0] == "GAME":
        display_game_state(s, response)
    elif response.split()[0] in ["END", "TIE"]:
        finish_game(s, response)
        # Search for new game after finishing
        search_for_game(s)
    elif response.split()[1] == "ERROR":
        place_error(s, response)
    else:
        # Message from server is not recognized, close connection and exit
        exit_error(s, response)


def game_exit(s):
    '''The player exits the server. It takes no argument. A player can issue this 
    command at any time. 
    Close the client socket and exit the program.'''
    # Send exit message to server
    send_msg(s, EXIT)

    # Receive confirmation
    responses = get_messages(s)
    
    for response in responses:
        if response == OK:
            # Close socket and exit client program
            print("Logging out.")
            s.close()
            sys.exit()
        elif response == QUIT:
            send_msg(s, QUIT)
            s.close()
            sys.exit()
        else:
            # Message from server is not recognized, close connection and exit
            exit_error(s, response)

def search_for_game(s):
    ''' Initiate game search '''
    send_msg(s, SEARCH)

    # TODO: Implement differences for Part 2
    response = s.recv(1024).decode()

    if response == OK:
        print("Searching for game ...")
    
    # Read from socket 
    # TODO: blocking socket until game happens
    
def handle_exit(s):
    # Ask if player wants to exit:
    while True:
        confirmation = input("Do you want to exit? Y/N")
        if confirmation == "Y":
            game_exit(s)
        elif confirmation == "N":
            search_for_game(s)
