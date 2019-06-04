import requests
from Modules.Required.Errorlog import errorlog


def load_apicalls(CLIENTID, CHANNELID):
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
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/follows()', "Userid:" + userid)


def id_to_username(userid: str) -> str:
    username = ""
    try:
        url = 'https://api.twitch.tv/helix/users?id=' + userid
        result = requests.get(url, headers=headers).json()
        username = result["data"][0]["display_name"]
        if username == "":
            return username
        else:
            username = result["data"][0]["login"]
            return username

    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/idtousername()', "Displayname:" + username)


def username_to_id(username: str) -> str:
    userid = ""
    try:
        url = 'https://api.twitch.tv/helix/users?login=' + username
        result = requests.get(url, headers=headers).json()
        userid = result["data"][0]["id"]
        return userid

    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/usernametoid()', "Userid:" + userid)


def channel_is_live() -> bool:
    result = ""
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
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/islive()', result)


def channel_game() -> str:
    response = ""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s/' % channel_id
        response = requests.get(url, headers=headers).json()
        game = response["game"]
        return game
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/channel_game()', response)



def get_modroom() -> (str, bool):
    rooms = {}
    url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
    response = requests.get(url, headers=headers).json()
    try:
        roomlist = response['rooms']
    except:
        roomlist = []
    for room in roomlist:
        rooms[room['name']] = room['_id']

    if "modlog" in rooms.keys():
        modroom_id = rooms['modlog']
        modroom_available = True
    else:
        modroom_id = None
        modroom_available = False
    return modroom_id, modroom_available
