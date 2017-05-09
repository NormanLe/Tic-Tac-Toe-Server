''' Constants for Response Code Strings and messages with no parameters '''

DELIM = "\r\n\r\n"

''' RESPONSE CODES '''
OK = "200 OK "
ERR400 = "400 ERROR "
ERR401 = "401 ERROR "
ERR402 = "402 ERROR "
ERR403 = "403 ERROR "
ERR404 = "404 ERROR "
ERR405 = "405 ERROR "
ERR406 = "406 ERROR "
ERR407 = "407 ERROR "

''' Other messages '''
EXIT = "EXIT "
QUIT = "QUIT "
SEARCH = "SEARCH "
WHO = "WHO "

''' Messages with parameters '''

def PLACE(n):
    return "PLACE " + str(n-1) + " "

def PLAY(name):
    return "PLAY " + name + " "

def LOGIN(name):
    return "LOGIN " + name + " "
