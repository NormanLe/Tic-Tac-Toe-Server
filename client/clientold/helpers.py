''' Various helper functions that may be used throughout client program 
'''
from socket import socket
import sys
from const import *


def exit_error(s, message):
    ''' Print error, close socket, and exit program upon receiving unexpected 
    messages from server'''
    print("Error: Response from Server does not match protocol.")
    print("Message from Server: " + message)
    print("Closing client socket and terminating program.")
    s.close()
    sys.exit()


def get_messages(s):
    ''' Return list of all messages (delimited by \r\n\r\n) in socket's buffer'''
    return s.recv(1024).decode().split(DELIM)

def quit_received(messages):
    ''' Return True if EXIT message found in list of received messages. False otherwise'''
    return QUIT in messages

def send_msg(s, msg_content):
    ''' Send message + \r\n\r\n on socket '''
    msg = msg_content + DELIM
    s.send(msg.encode())

