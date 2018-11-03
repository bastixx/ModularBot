import threading
import os

from Send_message import send_message
from Errorlog import errorlog


def load_bsmessage(FOLDER):
    global bsmessagestr; global backseating; global folder
    backseating = False
    folder = FOLDER

    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Backseatmessage.txt', 'r') as f:
            bsmessagestr = f.read()
    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Backseatmessage.txt', 'w') as f:
            bsmessagestr = "/me Please don't backseat. This is a blind playthrough!"
            f.write(bsmessagestr)


def bsmessage(s):
    global bstimer
    if backseating:
        try:
            bstimer = threading.Timer(10, bsmessage, [s])
            bstimer.start()
            send_message(s, bsmessagestr)
        except Exception as errormsg:
            errorlog(errormsg, "Backseatmessage()", '')


def backseatmessage(s, message):
    global bstimer; global bsmessagestr; global backseating
    messageparts = message.split(" ")
    if messageparts[1] == "on":
        backseating = True
        threading.Timer(10, bsmessage, [s]).start()
        send_message(s, "Backseating message enabled.")
    elif messageparts[1] == "off":
        try:
            backseating = False
            bstimer.cancel()
            send_message(s, "Backseating message disabled.")
        except:
            send_message(s, "Backseating message already off.")
    elif messageparts[1] == "set":
        try:
            newbsmessage = " ".join(messageparts[2:])
            bsmessagestr = newbsmessage
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Backseatmessage.txt', 'w') as f:
                f.write(bsmessagestr)
            send_message(s, "Backseat message changed.")
        except Exception as errormsg:
            errorlog(errormsg, 'backseatmessage/set()', message)
            send_message(s, "There was an error chaning the backseatmessage. Please try again.")
