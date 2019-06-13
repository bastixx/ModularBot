import requests
import logging

from Modules.Required.Sendmessage import send_message

logger = logging.getLogger(__name__)


def pun():
    try:
        joke = requests.get('https://icanhazdadjoke.com/', headers={"Accept": "application/json", "User-Agent": "Python - Requests"}).json()
        send_message(joke['joke'])
    except:
        logger.exception('')
        send_message('There was an error getting a pun. No laughing today :(')