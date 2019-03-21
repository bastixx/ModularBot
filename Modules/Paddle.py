import random

from Errorlog import errorlog
from Sendmessage import send_message


def paddle(displayname, message):
    try:
        messagesplit = message.split(" ")
        randint = random.randint(1, 20)
        if randint == 1:
            send_message("/timeout %s 5 Get paddled!" % messagesplit[1])
            send_message("%s got paddled so hard by %s they need a few seconds to recover..." %
                         (messagesplit[1].strip("@"), displayname))
        else:
            send_message("%s gets a paddling from %s! andyt90bat" %
                         (messagesplit[1].strip("@"), displayname))

    except KeyError:
        pass

    except Exception as errormsg:
        errorlog(errormsg, "!paddle", message)
