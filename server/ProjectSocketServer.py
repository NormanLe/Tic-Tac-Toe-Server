import queue
import threading
import sys

from ServerClasses import *

if __name__ == '__main__':
    HOST, PORT = 'localhost', 7000

    # Dictionary to hold games, with the key being the game ID
    games = {}
    # A queue to hold awaiting players
    user_queue = queue.Queue()
    # A dictionary to hold all players, either playing or waiting, with the keys being their file descriptor
    user_list = {}

    # Create the server, binding to localhost on port 7000
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPHandler, games, user_queue, user_list, threading.Lock(), 0)

    # Start a thread with the server -- that thread will then start one more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    print('The Server is ready to receive')

    # Activate the server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server is terminating")
        server.shutdown()
        server.server_close()
        sys.exit(0)
