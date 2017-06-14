import socketserver
import socket


from ServerFunctions import *


# Class for a threaded TCP Server with a custom constructor to pass in our data structures and lock
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, request_handler, games, user_queue, user_list, observers, lock, entry):
        super().__init__(server_address, request_handler)
        self.games = games
        self.user_queue = user_queue
        self.user_list = user_list
        self.observers = observers
        self.lock = lock
        self.entry = entry


# Handle method that'll be called for each client thread
class ThreadedTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Get the data structures and the lock from the server
        games = self.server.games
        user_queue = self.server.user_queue
        user_list = self.server.user_list
        observers = self.server.observers
        lock = self.server.lock
        client = self.request

        # Client thread should live until exit is called
        while True:
            try:
                messages = client.recv(1024).decode().split(' \r\n\r\n')
                # Filter out empty strings after splitting messages
                messages = [item for item in messages if len(item) > 0]
            except UnicodeDecodeError:
                continue
            except socket.error:
                continue
            for message in messages:
                args = message.split()
                # Either one or no arguments for most commands; in the form of COMMAND ARGUMENT
                # Two arguments for login; in the form COMMAND ARGUMENT FLAG
                command = args[0]
                fd = client.fileno()
                # Do something based on the command
                if command == 'LOGIN':
                    unique = True
                    for users in user_list.values():
                        if args[1] == users.name:
                            unique = False
                    if unique:
                        lock.acquire()
                        make_user(args[1], client, args[2], user_queue, user_list, self.server.entry)
                        # Entry represents their entry position in the server
                        self.server.entry += 1
                        lock.release()
                    else:
                        # Else, not a unique user ID
                        client.send(ERR401.encode())
                elif command == 'PLACE':
                    position = int(args[1])
                    if fd not in games:
                        # Game does not exist
                        client.send(ERR403.encode())
                    elif position < 0 or position > 8:
                        # Invalid position
                        client.send(ERR402.encode())
                    else:
                        # If it's not the client's turn
                        if user_list[fd] != games[fd].current_player:
                            client.send(ERR404.encode())
                            continue

                        # Check if position was occupied, if not place the piece in the corresponding game
                        if not put_piece(games[fd].board, position, user_list[fd].piece):
                            client.send(ERR405.encode())
                            continue
                        lock.acquire()
                        check_board_state(fd, games, user_list, position)
                        lock.release()
                elif command == 'EXIT':
                    lock.acquire()
                    if fd in user_list:
                        exit_player(client, games, user_queue, user_list)
                    lock.release()
                    break
                elif command == 'WHO':
                    lock.acquire()
                    # Send the client a string containing users available
                    client.send(('%s\r\n' % get_users(user_list)).encode())
                    lock.release()
                elif command == 'GAMES':
                    lock.acquire()
                    # Send the client a string containing active games and users in the games
                    client.send(('%s\r\n' % get_games(games)).encode())
                    lock.release()
                elif command == 'PLAY':
                    opponent = args[1]
                    if fd not in user_list:
                        client.send(ERR412.encode())
                        continue
                    if user_list[fd].state == BUSY:
                        client.send(ERR409.encode())
                        continue
                    elif opponent == user_list[fd].name:
                        client.send(ERR408.encode())
                        continue
                    else:
                        lock.acquire()
                        play_user(client, opponent, games, user_list, fd)
                        lock.release()
                elif command == 'OBSERVE':
                    # TODO: make sure observers see board correctly
                    gameid = int(args[1])
                    if fd in games:
                        client.send(ERR413.encode())
                        continue
                    elif fd not in user_list:
                        client.send(ERR417.encode())
                        continue
                    found = False
                    for game in games.values():
                        if gameid is game.p1.socket.fileno():
                            lock.acquire()
                            game.observer_list.append(client)
                            send_board([client], GAME, game.current_player, game.board)
                            observers[client] = game.observer_list
                            lock.release()
                            found = True
                            break
                    if not found:
                        client.send(ERR414.encode())
                    else:
                        user_queue.remove(user_list[fd])
                elif command == 'UNOBSERVE':
                    gameid = args[1]
                    if client not in observers:
                        client.send(ERR415.encode())
                    for key, game in games.items():
                        if key == gameid:
                            lock.acquire()
                            game.observer_list.remove(client)
                            del observers[client]
                            lock.release()
                            break
                elif client in observers:
                    if fd not in user_list:
                        client.send(ERR416.encode())
                    # send message to all observers in that game
                    send_message([x for x in observers[client] if x != fd], user_list[fd].name, message)
                elif command == '200':
                    continue
                else:
                    # Command was not recognizable
                    client.send(ERR400.encode())
                    continue
                # Start a game if there are at least two players
                if len(user_queue) > 1:
                    lock.acquire()
                    start_new_game(user_queue[0], user_queue[1], games)
                    del user_queue[0:2]
                    lock.release()
