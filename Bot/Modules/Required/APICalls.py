import requests
from Modules.Required.Errorlog import errorlog


def load_apicalls(CLIENTID, CHANNELID):
    global channel_id
    global client_id
    global headers
    channel_id = CHANNELID
    client_id = CLIENTID
    headers = {'Client-ID': client_id, 'Accept': 'application/json', 'Content-Type': 'application/json'}


def follows(userid):
    try:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channel_id)
        r = requests.get(url, headers=headers).json()

        # Returns data about when x follows y, or {} if x doesnt follow y
        return r.data[0]
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/follows()', "Userid:" + userid)


def id_to_username(userid):
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


def username_to_id(username):
    userid = ""
    try:
        url = 'https://api.twitch.tv/helix/users?login=' + username
        result = requests.get(url, headers=headers).json()
        userid = result["data"][0]["id"]
        return userid

    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/usernametoid()', "Userid:" + userid)


def channel_is_live():
    result = "Empty"
    try:
        url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
        response = requests.get(url, headers=headers).json()
        islive = response["data"][0]["type"]
        if islive == "live":
            return True
        else:
            return False
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/islive()', result)


def channel_game():
    url = 'https://api.twitch.tv/kraken/channels/%s/' % channel_id
    response = requests.get(url, headers=headers).json()
    game = response[0]["game"]
    return game


def get_modroom():
    rooms = {}
    url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
    response = requests.get(url, headers=headers).json()
    roomlist = response['rooms']
    for room in roomlist:
        rooms[room['name']] = room['_id']

    if "modlog" in rooms.keys():
        modroom_id = rooms['modlog']
        modroom_available = True
    else:
        modroom_id = None
        modroom_available = False
    return modroom_id, modroom_available
