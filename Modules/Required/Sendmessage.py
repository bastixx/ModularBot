from Required.Logger import logger
from Required.Errorlog import errorlog


def load_send_message(folder, channel, socket):
    global CHANNEL; global FOLDER; global s
    CHANNEL = channel
    FOLDER = folder
    s = socket


def send_message(message):
    try:
        s.send(b"PRIVMSG #%s :%s\r\n" % (CHANNEL, message.encode()))
        print(">>BOT : " + message)
        logger(">>BOT", message, False, True)
    except Exception as errormsg:
        errorlog(errormsg, "Send_message", message)
