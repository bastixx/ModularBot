from Modlog import *
from Required.Logger import *


def load_tagger(CLIENTID):
    global clientid
    clientid = CLIENTID


# def idlookup(userid):
#     url = 'https://api.twitch.tv/helix/users?id=' + userid
#     headers = {'Client-ID': clientid, 'Accept': 'application/json', 'Content-Type': 'application/json'}
#     result = requests.get(url, headers=headers).json()
#     displayname = result["data"][0]["display_name"]
#     username = result["data"][0]["login"]
#     return displayname, username


def tagprivmsg(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    ismod = tags.get("mod")
    issub = tags.get("subscriber")
    displayname = tags.get("display-name")
    userid = tags.get("user-id")

    # message
    try:
        message = lineparts[2].rstrip("\r")
    except:
        message = lineparts[1].rstrip("\r")

    # username
    try:
        username = lineparts[1].split("!")[0]
    except:
        username = "Undefined_username"
    return displayname, username, userid, message, issub, ismod


def tagclearchat(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value

    if len(lineparts) > 0:
        duration = tags.get("ban-duration")
    else:
        duration = 0

    userid = tags.get("target-user-id")
    username = lineparts[2]

    # displayname, username = idlookup(userid)
    modlog(duration, userid, username)


def tagclearmsg(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value

    message = lineparts[2]
    username = tags.get("login")
    userid = tags.get("user-id")

    removedmessage(username, userid, message)


def tagusernotice(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    message = lineparts[2]
    displayname = tags.get("display-name")
    ismod = tags.get("mod")
    issub = tags.get("subscriber")
    userid = tags.get("user-id")

    logger(userid, displayname, message, issub, ismod)


def tagnotice(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    message = lineparts[2]
    logger(0000000, "NOTICE", message, False, False, True)

# Unused for now.
# def taguserstate(line):
#     msgtype = "USERSTATE"
#     return msgtype
