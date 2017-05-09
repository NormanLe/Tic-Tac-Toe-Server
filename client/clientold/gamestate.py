''' Functions to handle placement errors and  display game state to the user.
'''

from const import *
from helpers import exit_error, send_msg, get_messages

def extract_game_state(s, message):
    words = message.split()
    if words[0] in ["GAME", "END"]:
        start_index = 2
    elif words[0] == "TIE":
        start_index = 1
    else:
        exit_error(s, message)

    game_state_list = []
    for i in range(start_index, start_index+9):
        game_state_list.append(words[i])
    if len(game_state_list) < 9:
        exit_error(s, message)
    return game_state_list

def print_gameboard(s, message):
    '''Helper function to print the game board'''
    game_state = extract_game_state(s, message)
    for i, letter in enumerate(game_state):
        print(letter, end='', flush=True)
        if i in [2, 5]:
            print("\n---")
        elif i == 8:
            print("\n")
        else:
            print("|")


def display_game_state(s, message):
    '''Display the game state, as in, parse the message into a human readable tic tac toe display
    '''
    print_gameboard(s, message)
    print("It's " + message.split()[1] + "'s turn.")


''' Display final game state and results upon receiving an END/TIE message'''
def finish_game(s, message):
    print_gameboard(s, message)
    if message.split()[0] == "END":
        print("The game has ended. " + message.split()[1] + "won!")
    elif message.split()[0] == "TIE":
        print("The game has ended. Tie game.")
    else:
        exit_error(s, message)
    
    # Send OK to server
    send_msg(s, OK)
    
    # TODO: handle new game after finishing
    print("")


''' Display error messages from the server related to PLACE '''
def place_error(s, message):
    if message == ERR402:
        print("Place Error: Position not in valid range 1-9. Try again")
    elif message == ERR403:
        print("Place Error: You aren't in a game")
    elif message == ERR404:
        print("Place Error: Not your turn")
    elif message == ERR405:
        print("Place Error: Illegal move, space occupied. Try again")
    else:
        exit_error(s, message)
