import random
import time

from Sendmessage import send_message
from Errorlog import errorlog


def roulette(displayname, s):
    try:
        randint = random.randint(1, 6)
        send_message("%s spins the gun and pulls the trigger.." % displayname)
        time.sleep(1)
        if randint == 1:
            send_message("The gun fires and %s drops dead to the ground!" % displayname)
            send_message("/timeout %s 1" % displayname)
        else:
            send_message("A CLICK can be heard as nothing happends. %s lives!" % displayname)
    except Exception as errormsg:
        errorlog(errormsg, "roulette()", '')
