from Errorlog import errorlog
from Send_message import send_message
import os
import requests


def bits(channel_id, client_id):
    # postponed untill i figure out why this requires authentication and how to implement.
    pass


def unshorten(s, shorturl):
    try:
        url = f'https://unshorten.me/json/https://{shorturl}'
        r = requests.get(url).json()
        longurl = r["resolved_url"]
        if shorturl not in longurl:
            send_message(s, f"This link expands to: {longurl}")
    except Exception as errormsg:
        errorlog(errormsg, "unshorten()", "")


def followergoal(s, channel_id, channel, client_id):
    try:
        url = f'https://api.twitch.tv/helix/users/follows?to_id={channel_id}'
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        total = r["total"]
        print(total)
        if int(total) % 250 == 0:
            send_message(s, f"@{channel.decode()} congrats on {total} followers!")
    except Exception as errormsg:
        errorlog(errormsg, "followergoals()", "")
