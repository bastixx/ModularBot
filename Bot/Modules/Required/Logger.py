from unidecode import unidecode
import time
import os
from pathlib import Path

from Modules.Required.Errorlog import errorlog


def load_logger(channelname):
    global file_path
    base_path = Path(__file__).parent
    file_path = (base_path / f"../../Data/{channelname}_errorlog.txt").resolve()


def logger(userid, displayname, message, issub, ismod, issystem=False):
    try:
        timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
        print(f"[{timestamp}] {displayname}: {message}")
        message = unidecode(message)

        with open(file_path, "a+") as f:
            f.write(f"timestamp: {timestamp}, displayname: {displayname}, userid: {userid}, message: {message}, "
                    f"sub: {issub}, mod: {ismod}, systemmessage: {issystem}")
        # insertone("Chatlog", {"timestamp": timestamp, "displayname": displayname, "userid": userid,
        #                           "message": message, "sub": issub, "mod": ismod, "systemmessage": issystem})

        return timestamp
    except Exception as errormsg:
        errorlog(errormsg, "Logger", message)


def logtofile(folder, func, line):
    now = str(time.strftime("%H:%M:%S"))
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Errorlog.txt", "a") as f:
        f.write(f"[{now}] [{func}]: {line}")
