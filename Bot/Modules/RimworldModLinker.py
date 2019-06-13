from bs4 import BeautifulSoup
import requests
import re
import json
import logging

from Modules.Required.Sendmessage import send_message

logger = logging.getLogger(__name__)


def linkmod(message):
    messagesplit = message.split(" ")
    
    if len(messagesplit) == 1:
        send_message('Usage: !linkmod <mod name or keywords>')
        return

    searchterm = "+".join(messagesplit[1:])

    try:
        r = requests.get(f'https://steamcommunity.com/workshop/browse/?appid=294100&searchtext={searchterm}&childpublishedfileid=0&browsesort=textsearch&section=items&requiredtags[]=Mod')
        webpage = r.text
        soup = BeautifulSoup(webpage, "html.parser")
        # for item in soup.find_all(re.compile("SharedFileBindMouseHover\(.+({.+})")):
        try:
            for item in soup.find_all("script"):
                itemtext = re.sub('[\\r\\t\\n]', '', item.text)
                if 'SharedFileBindMouseHover' in itemtext:
                    item = re.search('({.*})', itemtext)
                    jsonitem = json.loads(item.group(1))
                    modtitle = jsonitem['title']
                    modid = jsonitem['id']
                    break

            send_message(f'Found the mod: {modtitle} https://steamcommunity.com/sharedfiles/filedetails/?id={modid}')
        except:
            send_message("No mods found.")
    except:
        logger.exception('')
        send_message('An unexpected error occured. Please check your command and try again.')
