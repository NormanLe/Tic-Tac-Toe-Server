''' Module for reading and control flow of input from stdin
and data received from socket'''

import Commands
import MessageHandler


def parse_cmd(s, state):
    ''' Called when there is input available from STDIN. Check if user entered a valid command,
    and call the corresponding function. Alert user and print help if command is not recognized '''

    cmd = input()
    # If cmd is empty do nothing
    if len(cmd) == 0:
        return
    # Break command by spaces
    args = cmd.split()
    if args[0] == "help":
        Commands.help()
    elif args[0] == "login":
        if len(args) == 2:
            Commands.login(s, state, args[1], None)
        elif len(args) == 3:
            Commands.login(s, state, args[1], args[2])
        else:
            print("Incorrect number of arguments for login\n")
    elif args[0] == "place":
        if len(args) == 2:
            Commands.place(s, state, args[1])
        else:
            print("Incorrect number of arguments for place")
    elif args[0] == "exit":
        Commands.exit(s, state)
    elif args[0] == "games":
        Commands.games(s)
    elif args[0] == "who":
        Commands.who(s)
    elif args[0] == "play":
        if len(args) == 2:
            Commands.play(s, args[1])
        else:
            print("Incorrect number of arguments for play")
    elif args[0] == "observe":
        if len(args) == 2:
            Commands.observe(s, args[1])
        else:
            print("Incorrect number of arguments for observe")
    elif args[0] == "unobserve":
        if len(args) == 2:
            Commands.unobserve(s, args[1])
        else:
            print("Incorrect number of arguments for unobserve")
    else:
        Commands.message(s, args[0])


def read_socket(s, state):
    ''' Called when select says socket is ready to be read from .
    The messages we expect to receive from here are GAME, TIE
    QUIT, and FOUND. '''

    # Call recv on socket, split messages by delimiter, and queue them up
    s.recv_messages()

    # Retrieve first unprocessed message from queue
    message = s.read_message()

    # While there are unprocessed messages, process them
    while message:
        # Call appropriate Message Handling function depending on message structure
        if message == "" or message == " ":
            continue
        elif message.split()[0] == "QUIT":
            MessageHandler.handle_quit(s, state, message)
        elif message.split()[0] in ["TIE", "END"]:
            MessageHandler.handle_end(s, state, message)
        elif message.split()[0] == "GAME":
            MessageHandler.handle_game(s, state, message)
        elif message.split()[0] == "FOUND":
            MessageHandler.handle_found(s, state, message)
        elif message.split()[0] == "GAMEID":
            MessageHandler.handle_gameid(s, state, message)
        elif message.split()[0] == "USERS":
            MessageHandler.handle_users(s, state, message)
        elif message.split()[0] == "MSG":
            MessageHandler.handle_message(s, state, message)
        elif len(message.split()) > 1 and message.split()[1] == "ERROR":
            MessageHandler.handle_error(s, state, message)
        # Process the next message
        message = s.read_message()
