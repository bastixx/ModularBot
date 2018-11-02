import random
import time

from Send_message import send_message
from Errorlog import errorlog


def roulette(displayname, s):
    try:
        randint = random.randint(1, 6)
        send_message(s, "%s spins the gun and pulls the trigger.." % displayname)
        time.sleep(1)
        if randint == 1:
            send_message(s, "The gun fires and %s drops dead to the ground!" % displayname)
            send_message(s, "/timeout %s 1" % displayname)
        else:
            send_message(s, "A CLICK can be heard as nothing happends. %s lives!" % displayname)
    except exception as errormsg:
        errorlog(errormsg, "roulette()", '')
