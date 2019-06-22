import threading
import logging

from Modules.Required.Sendmessage import send_message
from Modules.Required.APICalls import channel_is_live, channel_game
import Modules.Required.Database as Database
# TODO Replace this module with a timed CustomCommand entry.

logger = logging.getLogger(__name__)


def load_rimworldautomessage() -> bool:
    global messagetext
    try:
        for document in Database.getall("RimworldAutomessage"):
            messagetext = document["messagetext"]
        return True
    except:
        logger.exception('Error loading Module. Module disabled.')
        messagetext = "/me If you want a colonist to be renamed to your username then join our raffle!" \
                      " Simply type '!join colonist' to enter!"
    finally:
        threading.Timer(300, rimworldautomessage).start()


def rimworldautomessage() -> None:
    game = channel_game()
    islive = channel_is_live()
    try:
        if islive and game == "RimWorld":
            send_message(messagetext)

    except IndexError:
        pass
    except:
        logger.exception('')
    finally:
        threading.Timer(900, rimworldautomessage).start()


def setmessage(message: str) -> None:
    global messagetext
    arguments = message.split(" ")
    try:
        if arguments[1] == "set":
            messagetext = " ".join(arguments[2:])
            Database.updateone("RimworldAutomessage", {}, {"messagetext": messagetext}, True)
            send_message("Message updated!")
    except:
        logger.exception(f'message: {message}')
        send_message("There was an error setting the message. Please check your command and try again.")
