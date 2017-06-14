import threading
import sys

from ServerClasses import *

if __name__ == '__main__':

    # Tell user if they did not provide enough arguments to the program
    if len(sys.argv) < 2:
        print("Error: not enough arguments provided")
        print("Provide a port")
        sys.exit()

    # Check that port is a number
    try:
        int(sys.argv[1])
    except ValueError:
        print("Error: The 1st argument (port) should be an integer.")
        sys.exit()

    HOST, PORT = 'localhost', int(sys.argv[1])

    # Create the server, binding to localhost on port 7000
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPHandler, {}, [], {}, {}, threading.Lock(), 0)

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
