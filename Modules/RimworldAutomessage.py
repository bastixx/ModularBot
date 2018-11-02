import threading
import requests

from Send_message import send_message
from Getgame import getgame
from Errorlog import errorlog


def load_rimworldautomessage(s, FOLDER, channelid, CLIENTID):
    global messagetext
    global channel_id
    global folder
    global client_id
    channel_id = channelid
    folder = FOLDER
    client_id = CLIENTID

    messagetext = "/me If you want a colonist to be renamed to your username then join our raffle! " \
                  "Simply type \"!join colonist\" to enter!"

    threading.Timer(300, rimworldautomessage, [s]).start()


def rimworldautomessage(s):
    game = getgame(channel_id, client_id)

    url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    response = r["data"]
    try:
        if response[0]["type"] == "live" and game == "RimWorld":
            send_message(s, messagetext)

    except IndexError:
        pass
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage", '')
    finally:
        threading.Timer(900, rimworldautomessage, [s]).start()
