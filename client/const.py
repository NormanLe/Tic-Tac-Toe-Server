''' Constants for Response Code Strings and outgoing messages '''

''' Delimiter for messages that follow our protocol '''
DELIM = " \r\n\r\n"

''' RESPONSE CODES '''
OK = "200 OK"
ERR400 = "400 ERROR"
ERR401 = "401 ERROR"
ERR402 = "402 ERROR"
ERR403 = "403 ERROR"
ERR404 = "404 ERROR"
ERR405 = "405 ERROR"
ERR406 = "406 ERROR"
ERR407 = "407 ERROR"
ERR408 = "408 ERROR"
ERR409 = "409 ERROR"
ERR410 = "410 ERROR"
ERR411 = "411 ERROR"
ERR412 = "412 ERROR"
ERR413 = "413 ERROR"
ERR414 = "414 ERROR"
ERR415 = "415 ERROR"
ERR416 = "416 ERROR"
ERR417 = "417 ERROR" 

''' Messages without parameters '''
EXIT = "EXIT"
QUIT = "QUIT"
SEARCH = "SEARCH"
WHO = "WHO"
GAMES = "GAMES"
MSG = "MSG"

''' Messages with parameters '''


def PLACE(n):
    return "PLACE " + str(n - 1)


def PLAY(name):
    return "PLAY " + name


def LOGIN(name, mode):
    if mode == None:
        mode = "A"
    return "LOGIN " + name + " " + mode

def OBSERVE(name):
    return "OBSERVE " + name


def UNOBSERVE(name):
    return "UNOBSERVE " + name
