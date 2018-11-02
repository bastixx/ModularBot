import random

from Errorlog import errorlog
from Send_message import send_message


def paddle(s, displayname, message):
    try:
        messagesplit = message.split(" ")
        randint = random.randint(1, 20)
        if randint == 1:
            send_message(s, "/timeout %s 5 Get paddled!" % messagesplit[1])
            send_message(s, "%s got paddled so hard by %s they need a few seconds to recover..." %
                         (messagesplit[1].strip("@"), displayname))
        else:
            send_message(s, "%s gets a paddling from %s! andyt90bat" %
                         (messagesplit[1].strip("@"), displayname))

    except KeyError:
        pass

    except Exception as errormsg:
        errorlog(errormsg, "!paddle", message)
