import threading
import logging

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errorlog import errorlog
import Modules.Required.Database as Database
from Modules.Required.APICalls import channel_is_live


def load_bsmessage() -> None:
    global bsmessagestr
    global backseating
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.ERROR)
    fh = logging.FileHandler(filename="Log.log", mode="a+")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
                                  datefmt='%d-%b-%y %H:%M:%S')

    sh.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(sh)
    logger.addHandler(fh)
    backseating = False

    try:
        bsmessagestr = Database.getone("Backseatmessage")["message"]
    except:
        logger.exception("")
        bsmessagestr = "/me Please don't backseat. This is a blind playthrough!"


def bsmessage() -> None:
    global bstimer
    global backseating
    if channel_is_live():
        if backseating:
            try:
                bstimer = threading.Timer(900, bsmessage)
                bstimer.start()
                send_message(bsmessagestr)
            except:
                logger.exception("")
    else:
        backseating = False


def backseatmessage(message) -> None:
    global bstimer
    global bsmessagestr
    global backseating
    messageparts = message.split(" ")
    if messageparts[1] == "on":
        if not backseating:
            backseating = True
            bstimer = threading.Timer(30, bsmessage)
            bstimer.start()
            send_message("Backseating message enabled.")
        else:
            send_message("Backseating message already enabled.")
    elif messageparts[1] == "off":
        if backseating:
            backseating = False
            bstimer.cancel()
            send_message("Backseating message disabled.")
        else:
            send_message("Backseating message already disabled.")
    elif messageparts[1] == "set":
        try:
            newbsmessage = " ".join(messageparts[2:])
            bsmessagestr = newbsmessage

            # Empty filter will match all elements,
            # but since there will be only 1 element in the database this won't be an issue.
            Database.updateone("Backseatmessage", {}, {"message": bsmessagestr}, True)
            send_message("Backseat message changed.")
        except:
            logger.exception(f"Message: {message}")
            send_message("There was an error changing the backseatmessage. Please try again.")
