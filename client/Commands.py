''' Functions to support commands input by user.
'''
from const import *
import MessageHandler
import sys

def help():
    ''' This command takes no argument. It prints a list of supported commands, which are ones in
    this list. For each command, it prints a brief description of the command function and
    the syntax of usage
    '''
    print("Supported commands:")
    print("help : Print a list of supported commands")
    print("login [name] [mode]: Login to the game server. Takes 2 arguments, [name] and [mode], A for automatch, M for automatch off")
    print("place [n] : Issues a move. Takes one argument [n], which is between 1 and 9 inclusive")
    print("exit : Exit the server")
    print("who : List all players logged in")
    print("games : List all ongoing games")
    print("play [name] : Request to play a user. Takes one argument, [name] of player to request\n")


def login(s, state, name, mode):
    ''' This command takes one argument, your name. A player name is a userid that uniquely
    identifies a player. Your name is entered with this command and is sent to the server.
    Return True if login success, False if login failed.'''
    if mode is None:
        mode = 'A'

    if mode and mode not in ['A', 'M']:
        print("Mode must be A or M\n")
        return

    # Send message to server
    s.send(LOGIN(name, mode))

    # Receive response message from server
    s.recv_messages()

    # Check response from server
    response = s.read_message()
    while response:
        if response in [OK, ERR401]:
            MessageHandler.handle_login(s, state, response, name, mode)
            return
        else:
            MessageHandler.handle_unrecognized(s, state, response)
        response = s.read_message()

def place(s, state, n):
    '''This command issues a move. It takes one argument n, which is between 1 and 9 inclusive.
    It identify a cell that the player chooses to occupy at this move. 
    If all is well, the new game state is received from the server and displayed.'''
    try:
        n = int(n)
    except ValueError:
        print("place must be called with an integer argument\n")
        return
    # Send place message to server
    s.send(PLACE(n))

def exit(s, state):
    ''' This command allows player to exit '''
    # Check if player logged in:
    # if not state.logged_in:
    #     print("You are not logged in.\n")
    #     return

    # Send exit message to server
    s.send(EXIT)

    print("Exiting ... \n")

    sys.exit()

    # Note: Remaining code won't execute/matter,
    # Since server will close connection immediately.

    # Update state
    state.initiated_exit = True
    state.clear_game()

    s.recv_messages()
    response = s.read_message()
    # Exit can be received from main
    while response:
        if response in [OK, QUIT]:
            MessageHandler.handle_quit(s, state, response)
        response = s.read_message()


def games(s):
    s.send(GAMES)
    # nothing else needs to be done, just wait for response

def who(s):
    s.send(WHO)
    # nothing else needs to be done, just wait for response

def play(s, name):
    s.send(PLAY(name))
    # nothing else needs to be done, just wait for found/error
