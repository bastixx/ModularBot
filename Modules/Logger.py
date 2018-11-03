from unidecode import unidecode
import time
import os

from Errorlog import errorlog


def load_logger(FOLDER):
    global folder
    folder = FOLDER
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y")
              + ".txt", 'w'):
        pass


def logger(displayname, message, issub, ismod):
    sub = ""
    mod = ""
    if issub:
        sub = "|SUB"
    if ismod:
        mod = "|MOD"

    try:
        message = unidecode(message)
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y") + ".txt", 'a+') as f:
            f.write("[%s] %s: %s %s%s\n" % (str(time.strftime("%H:%M:%S")), displayname, message, sub, mod))
    except Exception as errormsg:
        errorlog(errormsg, "Logger", message)
