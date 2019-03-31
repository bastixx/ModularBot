from unidecode import unidecode
import time
import os

from Required.Errorlog import errorlog
from Required.Database import insertoneindb


def logger(displayname, message, issub, ismod):
    try:
        message = unidecode(message)
        insertoneindb("Chatlog", {"timestamp": str(time.strftime("%d-%m-%Y %H:%M:%S")), "displayname": displayname,
                                  "message": message, "sub": issub, "mod": ismod})

    except Exception as errormsg:
        errorlog(errormsg, "Logger", message)


def logtofile(folder, func, line):
    now = str(time.strftime("%H:%M:%S"))
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Log.txt", "a") as f:
        f.write(f"[{now}] [{func}]: {line}")
