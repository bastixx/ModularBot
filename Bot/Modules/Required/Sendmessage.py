from Modules.Required.Logger import chatlogger
import logging

logger = logging.getLogger(__name__)


def load_send_message(folder, channel, socket):
    global CHANNEL; global FOLDER; global s
    CHANNEL = channel
    FOLDER = folder
    s = socket


def send_message(message):
    try:
        s.send(b"PRIVMSG #%s :%s\r\n" % (CHANNEL, message.encode()))
        chatlogger(str(0000000), ">>BOT", message)
    except:
        logger.exception(f'message: {message}')