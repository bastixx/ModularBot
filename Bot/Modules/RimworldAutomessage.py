import threading

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errorlog import errorlog
from Modules.Required.APICalls import channel_is_live, channel_game
import Modules.Required.Database as Database
# TODO Replace this module with a timed CustomCommand entry.


def load_rimworldautomessage() -> None:
    global messagetext
    try:
        for document in Database.getall("RimworldAutomessage"):
            messagetext = document["messagetext"]
    except:
        messagetext = "/me If you want a colonist to be renamed to your username then join our raffle!" \
                      " Simply type '!join colonist' to enter!"
    threading.Timer(300, rimworldautomessage).start()


def rimworldautomessage() -> None:
    game = channel_game()
    islive = channel_is_live()
    try:
        if islive and game == "RimWorld":
            send_message(messagetext)

    except IndexError:
        pass
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage", '')
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
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage/setmessage()", message)
        send_message("There was an error setting the message. Please check your command and try again.")
