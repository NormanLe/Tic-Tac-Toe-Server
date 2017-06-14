''' Classes to be used by client program '''

import sys
from collections import deque
from socket import socket, AF_INET, SOCK_STREAM

from const import *


class TTTSocket():
    ''' Wrapper for a TCP socket for TicTacToe game. Will automatically
    append protocol delimiter to end of messages, and encode messages
    to bytes. Also will read messages delimited by provided delim to
    handle multiple messages in buffer '''

    def __init__(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.delim = DELIM
        self.recvd_msgs = deque()

    def connect(self, server_name, server_port):
        '''Connect to specified server name and server port'''
        self.s.connect((server_name, server_port))

    def close(self):
        ''' Close socket '''
        self.s.close()

    def send(self, message):
        '''Send message as string, delimiter will be added'''
        message = message + self.delim
        self.s.send(message.encode())

    def read_message(self):
        ''' Return next message from queue of messages to be processed'''
        if len(self.recvd_msgs) == 0:
            return None
        return self.recvd_msgs.popleft()

    def recv_messages(self):
        ''' Retrieve messages from socket and store in list'''
        # debug
        raw = self.s.recv(1024).decode()
        # Printing un trimmed / split message from socket for debugging
        if len(sys.argv) == 4 and sys.argv[3] == "DEBUG":
            print("-------------------------")
            print("raw message: \n" + raw)
            print("-----------------------\n")
        new_messages = raw.split(DELIM)
        # Filter empty messages
        new_messages = [item for item in new_messages if len(item) > 0]
        if new_messages is None or len(new_messages) == 0:
            print("Connection was closed or error occured")
            self.s.close()
            sys.exit()
        self.recvd_msgs.extend(new_messages)


class ClientState():
    ''' Maintain state of client to appropraitely respond to
    incoming messages from server '''

    def __init__(self):
        self.logged_in = False
        self.found_game = False
        self.in_game = False
        self.is_turn = False
        self.initialized_exit = False
        self.mark = None
        self.name = ""
        self.opponent = ""
        self.is_observer = False
        # Mode: A for automatch, M for not automatch (part 2). Specified at login
        self.mode = ""

    def clear_game(self):
        self.is_turn = False
        self.in_game = False
        self.mark = None
        self.is_observer = False


class GameState():
    """ This class is constructed by an incoming GAME, END, or TIE message
    and contains methods to parse the message and display the current status
    of the game """

    def __init__(self, state, message):
        self.turn = None
        self.finished = False
        self.tie = False
        self.winner = None
        self.parse_game_msg(message)
        self.state = state

    def parse_game_msg(self, message):
        """ Initialize GameState object by parsing GAME message """
        words = message.split()
        start_index = 2
        game_state_list = []

        for i in range(start_index, start_index + 9):
            game_state_list.append(words[i])
        if len(game_state_list) < 9:
            pass
        self.board = game_state_list

        if words[0] == "GAME":
            self.turn = words[1]
        elif words[0] in ["TIE", "END"]:
            self.finished = True
            if words[0] == "TIE":
                self.tie = True
            else:
                self.winner = words[1]

    def display_game_board(self):
        ''' Takes sequence of E/X/O and prints out a game board '''
        grid = self.board
        for i, letter in enumerate(grid):
            print(letter, end='', flush=True)
            if i in [2, 5]:
                print("\n-----")
            elif i == 8:
                print("\n")
            else:
                print("|", end='', flush=True)
        sys.stdout.flush()

    def show_game(self):
        """ Show the game board and whos turn it is, or the outcome if it's ended already """
        self.display_game_board()

        # If game isn't finished, say who's turn it is. Else, display Tie/Winner info
        if not self.finished:
            print("It's " + self.turn + "'s turn.\n")
        else:
            if self.tie:
                print("Tie Game.\n")
            else:
                if self.winner == self.state.name:
                    print("Congratulations! You win.\n")
                else:
                    print("Game over. " + self.winner + " won.\n")
