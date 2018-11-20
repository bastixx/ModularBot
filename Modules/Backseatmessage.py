import threading
import os
import requests

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
            bstimer = threading.Timer(60, bsmessage, [s])
            bstimer.start()
            send_message(s, bsmessagestr)
        except Exception as errormsg:
            errorlog(errormsg, "Backseatmessage()", '')


def backseatmessage(s, message):
    global bstimer; global bsmessagestr; global backseating
    messageparts = message.split(" ")
    if messageparts[1] == "on":
        if not backseating:
            backseating = True
            bstimer = threading.Timer(60, bsmessage, [s])
            bstimer.start()
            send_message(s, "Backseating message enabled.")
        else:
            send_message(s, "BSM already enabled.")
    elif messageparts[1] == "off":
        if backseating:
            backseating = False
            bstimer.cancel()
            send_message(s, "Backseating message disabled.")
        else:
            send_message(s, "BSM already off.")
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


def bsmcheck(channel_id, client_id):
    global backseating
    url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    response = r["data"]
    try:
        if response[0]["type"] == "live":
            pass
    except:
        backseating = False
