import socket

from Logger import logger
from Errorlog import errorlog


def load_send_message(folder, channel):
    global CHANNEL; global FOLDER
    CHANNEL = channel
    FOLDER = folder


def send_message(s, message):
    try:
        s.send(b"PRIVMSG #%s :%s\r\n" % (CHANNEL, message.encode()))
        print(">>BOT : " + message)
        logger(">>BOT", message, False, True)
    except Exception as errormsg:
        errorlog(errormsg, "Send_message", message)
