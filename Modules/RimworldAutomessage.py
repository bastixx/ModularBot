import threading
import requests

from Required.Sendmessage import send_message
from Required.Getgame  import getgame
from Required.Errorlog import errorlog
from Required.Database import *


def load_rimworldautomessage(channelid, CLIENTID):
    global messagetext
    global channel_id
    global client_id
    channel_id = channelid
    client_id = CLIENTID

    cursor = getallfromdb("RimworldAutomessage")
    for document in cursor:
        messagetext = document["messagetext"]
    threading.Timer(300, rimworldautomessage).start()


def rimworldautomessage():
    game = getgame(channel_id, client_id)

    url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    response = r["data"]
    try:
        if response[0]["type"] == "live" and game == "RimWorld":
            send_message(messagetext)

    except IndexError:
        pass
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage", '')
    finally:
        threading.Timer(900, rimworldautomessage).start()
