from ServerClasses import *
from ServerConst import *


# Every user is created with a name to identify them
# And a flag that represents whether or not they want auto-matching
class User(object):
    def __init__(self, name, fd, match_flag, entry):
        self.name = name
        self.socket = fd
        self.match_flag = match_flag
        self.entry = entry
        self.state = AVAILABLE

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


# Every game is initialized with two players
class Game(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        # Users are set to busy when game is created, and assigned the piece they use
        p1.state = BUSY
        p2.state = BUSY
        self.observer_list = []

        if p1.entry < p2.entry:
            self.current_player = p1
            p1.piece = X
            p2.piece = O
        else:
            self.current_player = p2
            p1.piece = O
            p2.piece = X
        # 2D List to represent a 3 by 3 board
        self.board = [[E for x in range(3)] for y in range(3)]


# Given a board, find the position, and assign the piece to the correct position
# Position is 0 based, so valid numbers are 0-8
# 2 is [0][2] 3 is [1][0] and 4 is [1][1], etc.
def put_piece(board, position, piece):
    x = int(position / 3)
    y = int(position - x * 3)
    if board[x][y] == E:
        board[x][y] = piece
        return True
    else:
        return False


def send_to_players(sockets, state, string):
    for player_socket in sockets:
        player_socket.send(('%s %s \r\n\r\n' % (state, string)).encode())


# Send the description of the board to both players
def send_board(sockets, state, current_player, board):
    send_to_players(sockets, state, '%s %s' % (current_player.name, translate_board(board)))


# Check if there is a winner - return t
def game_finished(board, position):
    x = int(position / 3)
    y = int(position - x * 3)

    if board[x][0] == board[x][1] == board[x][2]:
        return True
    elif board[0][y] == board[1][y] == board[2][y]:
        return True
    elif x == y and board[0][0] == board[1][1] == board[2][2]:
        return True
    elif x + y == 2 and board[0][2] == board[1][1] == board[2][0]:
        return True
    return False


# Get the representation of the board as a String containing E's, O's and X's
def translate_board(board):
    board_description = ''
    for x in range(len(board)):
        for y in range(len(board[0])):
            board_description += board[x][y] + ' '
    return board_description


# Find the other player in the game
def find_other_player(games, user_list, fd):
    if user_list[fd] == games[fd].p1:
        return games[fd].p2
    return games[fd].p1


# End the game, given the player who entered a command that resulted in that (EXIT or PLACE)
def end_game(games, fd):
    games[fd].p1.state = AVAILABLE
    games[fd].p2.state = AVAILABLE
    p1, p2 = games[fd].p1, games[fd].p2
    del games[p1.socket.fileno()]
    del games[p2.socket.fileno()]
    return (p1, p2)


# Return all available users as a string
def get_users(user_list):
    users_description = 'USERS '
    for user in user_list.values():
        if user.state == AVAILABLE:
            users_description += user.name + ' \r\n'
    return users_description


# Return all game descriptions
def get_games(games_list):
    games = 'GAMEID '
    for key, game in games_list.items():
        # Assuming it's an actual name
        if game.p1.name not in games:
            games += '%s %s %s' % (key, game.p1.name, game.p2.name) + ' \r\n'
    return games


def make_user(name, client_socket, flag, user_queue, user_list, position):
    # Create a user and add him to the list of users, and into the queue if they have auto-matching
    new_user = User(name, client_socket, flag, position)
    if flag == 'A':
        user_queue.append(new_user)
    user_list[client_socket.fileno()] = new_user
    client_socket.send(OK.encode())


def start_new_game(p1, p2, games):
    # Remove players from queue, and add them to game
    g = Game(p1, p2)

    games[p1.socket.fileno()] = g
    games[p2.socket.fileno()] = g
    # Players are told the user ID of the other player
    p1.socket.send(('FOUND %s %s \r\n\r\n' % (g.p2.name, g.p2.piece)).encode())
    p2.socket.send(('FOUND %s %s \r\n\r\n' % (g.p1.name, g.p1.piece)).encode())
    # Send board to both players and await moves
    send_board([p1.socket, p2.socket], GAME, g.current_player, g.board)


def check_board_state(fd, games, user_list, position):
    # Find the other player in the game
    games[fd].current_player = find_other_player(games, user_list, fd)
    temp_list = games[fd].observer_list[:]
    # Check if game is done after placed
    if game_finished(games[fd].board, position):
        mode = END
    elif not any(E in rows for rows in games[fd].board):
        mode = TIE
    else:
        mode = GAME
    temp_list.extend([games[fd].p1.socket, games[fd].p2.socket])
    send_board(temp_list, mode, games[fd].current_player, games[fd].board)
    if mode is not GAME:
        p1, p2 = end_game(games, fd)
        if p1.match_flag != "M":
            start_new_game(p1, p2, games)


def exit_player(client, games, user_queue, user_list):
    fd = client.fileno()
    if fd in games:
        # Find the player who didn't leave, and if he was in a game, put him back in queue if he wants auto-match
        staying_player = find_other_player(games, user_list, fd)
        if staying_player.state == BUSY:
            user_list[staying_player.socket.fileno()].state = AVAILABLE
        if user_list[staying_player.socket.fileno()].match_flag == 'A':
            user_queue.append(user_list[staying_player.socket.fileno()])
        # SEND QUIT AND OK to respective players
        staying_player.socket.send(QUIT.encode())
        user_list[fd].socket.send(OK.encode())
        # Remove user and game from dictionaries
        del games[fd]
        del games[staying_player.socket.fileno()]
    else:
        # Just logging out
        client.send(b"")
        # Remove from queue, they should be only one in the queue if auto-match is on, otherwise they aren't in queue
        if user_list[fd].match_flag == 'A':
            del user_queue[0]
    del user_list[fd]


def play_user(client, opponent, games, user_list, fd):
    target_player = None
    for key, user in user_list.items():
        if opponent == user.name and user.state == AVAILABLE:
            target_player = user
            break
    if target_player is None:
        client.send(ERR406.encode())
    elif target_player.state == BUSY:
        client.send(ERR407.encode())
    elif target_player.match_flag == 'A':
        client.send(ERR410.encode())
    elif user_list[fd].match_flag == 'A':
        client.send(ERR411.encode())
    else:
        start_new_game(user_list[fd], target_player, games)


def send_message(observers, name, message):
    for player_socket in observers:
        player_socket.send(('%s %s %s \r\n\r\n' % (MSG, name, message)).encode())
