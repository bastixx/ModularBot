from bs4 import BeautifulSoup
import requests
import re
import json

from Errorlog import errorlog
from Send_message import send_message


def load_mod(STEAMAPIKEY):
    global steamAPIkey
    steamAPIkey = STEAMAPIKEY


def linkmod(s, message):
    messagesplit = message.split(" ")
    searchterm = "+".join(messagesplit[1:])

    try:
        r = requests.get(f'https://steamcommunity.com/workshop/browse/?appid=294100&searchtext={searchterm}&childpublishedfileid=0&browsesort=textsearch&section=items&requiredtags[]=Mod')
        webpage = r.text
        soup = BeautifulSoup(webpage, "html.parser")
        # for item in soup.find_all(re.compile("SharedFileBindMouseHover\(.+({.+})")):
        for item in soup.find_all("script"):
            itemtext = re.sub('[\\r\\t\\n]', '', item.text)
            if 'SharedFileBindMouseHover' in itemtext:
                item = re.search('({.*})', itemtext)
                jsonitem = json.loads(item.group(1))
                modtitle = jsonitem['title']
                modid = jsonitem['id']
                break

        try:
            send_message(s, f'Found the mod: {modtitle} https://steamcommunity.com/sharedfiles/filedetails/?id={modid}')
        except:
            send_message(s, "No mods found.")
    except Exception as errormsg:
        errorlog(errormsg, "ModSearch()", "")
