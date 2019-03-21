from unidecode import unidecode
import time

from Errorlog import errorlog
from Database import insertoneindb


def logger(displayname, message, issub, ismod):
    try:
        message = unidecode(message)
        insertoneindb("Chatlog", {"timestamp": str(time.strftime("%H:%M:%S")), "displayname": displayname,
                                  "message": message, "sub": issub, "mod": ismod})

    except Exception as errormsg:
        errorlog(errormsg, "Logger", message)
