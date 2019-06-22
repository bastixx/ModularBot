from unidecode import unidecode
import time
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_logger(channelname: str) -> None:
    try:
        global file_path
        base_path = Path(__file__).parent
        file_path = (base_path / f'../../Data/{channelname}/chatlog-{str(time.strftime("%d-%m-%Y"))}.log').resolve()
    except:
        logger.exception('')
        raise Exception


def chatlogger(userid: str, displayname: str, message: str) -> str:
    try:
        timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
        print(f"[{timestamp}] {displayname}: {message}")
        message = unidecode(message)

        with open(file_path, "a+", encoding='UTF-8') as f:
            f.write(f"{timestamp},{displayname},{userid},{message}\n")

        return timestamp
    except:
        logger.exception('')


# Currently unused. Not updated yet.
def logtofile(folder, func, line):
    now = str(time.strftime("%H:%M:%S"))
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Errorlog.txt", "a") as f:
        f.write(f"[{now}] [{func}]: {line}")
