''' Module containing functions for handling messages '''
import sys

from ClientClasses import GameState
from const import *

''' The messages below can be received while waiting on a socket,
or at any other time '''


def handle_quit(s, state, message):
    ''' Handle QUIT messages '''
    # Check if you initialized quit
    # If so, send QUIT
    # 200 OK case: you were available
    if state.initialized_exit and message == OK:
        # close connection and exit program
        print("Confirmation received, exiting program.")
        s.close()
        sys.exit()
    elif state.initialized_exit and message == QUIT:
        print("Confirmation received, exiting program.")
        s.send(QUIT)
        s.close()
        sys.exit()
    elif not state.initialized_exit and message == QUIT:
        s.send(OK)
        state.clear_game()
        print("Other player quit the game.")
        if state.mode == 'A':
            print("Searching for new game ...\n")


def handle_game(s, state, message):
    ''' Handle GAME messages '''
    # # TODO: Check if state is valid to receive game message
    # if not state.found_game:
    #     print("Game message received unexpectedly. ")

    # Initialize state to game parameters if not set
    if not state.in_game and not state.is_observer:
        state.found_game = False  # clear found field because starting
        state.in_game = True
        state.mark = "X" if message.split()[1] == state.name else "O"
        print("Game started.")
        print("Your mark is " + state.mark + ".\n")

    if not state.is_observer:
        # Initialize turn
        state.is_turn = True if message.split()[1] == state.name else False

    # Display Game
    game = GameState(state, message)
    game.show_game()


def handle_end(s, state, message):
    ''' Handle END and TIE messages '''
    # Check if state is valid to receive game message
    if not state.in_game:
        print("error: how r u ending a game without starting")

    # Clear state parameters related to game
    state.clear_game()

    # Display Game results
    game = GameState(state, message)
    game.show_game()

    # Confirm receipt:
    s.send(OK)

    # Client will be available
    if state == 'A':
        print("Searching for game ... \n")


def handle_found(s, state, message):
    ''' Handle FOUND (info about game before it starts ) messages '''
    # respond with OK
    s.send(OK)

    # Update state
    state.opponent = message.split()[1]
    state.found_game = True

    # Display information
    print("Game found vs " + message.split()[1] + "\n")


def handle_users(s, state, message):
    ''' Handle USERS message (response to who) and print out a list of available users '''
    # Trim start of message: assuming messsage ends with " \r\n\r\n"
    message = message[6:]
    users = message.split(" \r\n")

    # TODO: confirm available users are being sent
    print("List of available logged in users:")
    for user in users:
        print(user)


def handle_gameid(s, state, message):
    ''' Handle GAMEID message'''
    # Trim start of message: assuming message ends with " \r\n\r\n"
    message = message[7:]
    # Split each game tuple into a list of game tuples
    games = message.split(" \r\n")
    # Print table header
    print("List of Games")
    if len(games) < 2:
        words = games[0].split()
        if len(words) == 3:
            print("GameID\tUser1\tUser2")
            print(words[0] + "\t" + words[1] + "\t" + words[2])
        else:
            print("No games are currently being played.")
        return

    print("GameID\tUser1\tUser2")
    # Print ID, User1, User2 for each game
    for game in games:
        game_id, name1, name2 = game.split()
        print(game_id + "\t" + name1 + "\t" + name2)
    print("\n")


def handle_unrecognized(s, state, message):
    ''' Handle unrecognized messages '''
    print("Ignoring unrecognized message: " + message)


''' The messages below should only be received while waiting on socket'''


def handle_error(s, state, message):
    ''' HANDLE 402-405 Errors '''
    if message == ERR402:
        print("Error, Invalid Response\n")
    elif message == ERR402:
        print("Error, attempt to place in an invalid slot\n")
    elif message == ERR403:
        print("Error, attempt to place but not in a game\n")
    elif message == ERR404:
        print("Error, attempt to place but not your turn\n")
    elif message == ERR405:
        print("Error, attempt to place in occupied slot\n")
    elif message == ERR406:
        print("Error, specified user does not exist\n")
    elif message == ERR407:
        print("Error, specified user is busy/unavailable\n")
    elif message == ERR408:
        print("Error, you can't play against yourself\n")
    elif message == ERR409:
        print("Error, you're already in a game\n")
    elif message == ERR410:
        print("Error, you can't challenge a player logged in on Automatch mode\n")
    elif message == ERR411:
        print("Error, you can't use the play command when logged in on Automatch mode\n")
    elif message == ERR412:
        print("Error, you can't use the play command when not logged in\n")
    elif message == ERR413:
        print("Error, can't observe when you're in a game\n")
    elif message == ERR414:
        print("Error, game does not exist so it cannot be observed\n")
    elif message == ERR415:
        print("Error, can't use the unobserve command when you weren't observing a game\n")
    elif message == ERR416:
        print("Error, can't chat without being logged in and spectating a game\n")
    elif message == ERR417:
        print("Error, can't observe without being logged in\n")
    else:
        print("Unidentified error: " + message + "\n")


def handle_login(s, state, message, name, mode):
    ''' Handle Response to LOGIN '''
    if message == OK:
        state.name = name
        state.logged_in = True
        print("Logged in as: " + name + "\n")
        if mode == "A":
            print("Searching for game ... \n")
            state.mode = "A"
        else:
            state.mode = "M"
    if message == ERR401:
        print("Login failure. Try a different name\n")

def handle_message(s, state, message):
    message = message.split()
    print(message[1], ':', end = '', flush = True)
    print(message[2] if len(message) == 3 else '')
