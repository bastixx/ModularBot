import requests
import logging
from Modules.Required.Errorlog import errorlog

logger = logging.getLogger(__name__)


def load_apicalls(CLIENTID: str, CHANNELID: str) -> None:
    global channel_id
    global client_id
    global headers
    channel_id = CHANNELID
    client_id = CLIENTID

    # Using V5 of the API.
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}

    # Not sure if content-type is neccecary.
    # headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json',
    #            'Content-Type': 'application/json'}


def follows(userid: str) -> dict:
    try:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channel_id)
        r = requests.get(url, headers=headers).json()

        # Returns data about when x follows y, or {} if x doesnt follow y
        return r.data[0]
    except:
        logger.exception("")
        raise Exception


def id_to_username(userid: str) -> str:
    try:
        url = 'https://api.twitch.tv/helix/users?id=' + userid
        result = requests.get(url, headers=headers).json()
        username = result["data"][0]["display_name"]
        if username == "":
            return username
        else:
            username = result["data"][0]["login"]
            return username

    except:
        logger.exception("")
        raise Exception


def username_to_id(username: str) -> str:
    try:
        url = 'https://api.twitch.tv/helix/users?login=' + username
        result = requests.get(url, headers=headers).json()
        userid = result["data"][0]["id"]
        return userid

    except:
        logger.exception("")
        raise Exception


def channel_is_live() -> bool:
    try:
        url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
        response = requests.get(url, headers=headers).json()
        if len(response["data"]) != 0:
            islive = response["data"][0]["type"]
        else:
            islive = ""
        if islive == "live":
            return True
        else:
            return False
    except:
        logger.exception("")
        raise Exception


def channel_game() -> str:
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s/' % channel_id
        response = requests.get(url, headers=headers).json()
        game = response["game"]
        return game
    except:
        logger.exception("")


def get_modroom() -> (str, bool):
    try:
        rooms = {}
        url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
        response = requests.get(url, headers=headers).json()
        try:
            roomlist = response['rooms']
        except:
            roomlist = []
        for room in roomlist:
            rooms[room['name']] = room['id']

        if "modlog" in rooms.keys():
            modroom_id = rooms['modlog']
            modroom_available = True
        else:
            modroom_id = None
            modroom_available = False
        return modroom_id, modroom_available
    except:
        logger.exception('')
        raise Exception
