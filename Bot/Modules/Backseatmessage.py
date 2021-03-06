import threading
import logging

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database
from Modules.Required.APICalls import channel_is_live

logger = logging.getLogger(__name__)


def load_bsmessage() -> None:
    global bsmessagestr
    global backseating
    global bstime
    bstime = 900

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
                bstimer = threading.Timer(bstime, bsmessage)
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
    global bstime
    arguments = message.split(" ")
    if arguments[1] == "on":
        if not backseating:
            backseating = True
            bstimer = threading.Timer(30, bsmessage)
            bstimer.start()
            send_message("Backseating message enabled.")
        else:
            send_message("Backseating message already enabled.")
    elif arguments[1] == "off":
        if backseating:
            backseating = False
            bstimer.cancel()
            send_message("Backseating message disabled.")
        else:
            send_message("Backseating message already disabled.")
    elif arguments[1] == "set":
        try:
            newbsmessage = " ".join(arguments[2:])
            bsmessagestr = newbsmessage

            # Empty filter will match all elements,
            # but since there will be only 1 element in the database this won't be an issue.
            Database.updateone("Backseatmessage", {}, {"message": bsmessagestr}, True)
            send_message("Backseat message changed.")
        except:
            logger.exception(f"Message: {message}")
            send_message("There was an error changing the backseatmessage. Please try again.")
    elif arguments[1] == "timer":
        try:
            if arguments[2].isdigit():
                send_message(f"Timer changed. Changed timer from {bstime} to {str(arguments[2])} seconds")
                bstime = arguments[2]
            else:
                send_message("arguments")
        except:
            send_message("There was an error updating the timer. Please check your command and try again.")
            logger.exception("")

