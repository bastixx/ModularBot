import requests
import time
from Required.Database import *

from Required.Errorlog import errorlog


# Try and get the ID for the mod channel. This is used for the moderation log.
def load_modlog(CHANNEL_ID, headers, FOLDER):
    global modroom_available
    global modroom_id
    global channel_id
    global folder
    channel_id = CHANNEL_ID
    folder = FOLDER
    rooms = {}
    try:
        url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
        r = requests.get(url, headers=headers).json()
        roomlist = r['rooms']
        for room in roomlist:
            rooms[room['name']] = room['_id']
        modroom_id = rooms['modlog']
        modroom_available = True
    except:
        modroom_available = False
        print(">>>No room to post modlog found.")


def modlog(parts):
    timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
    issub = False
    ismod = False
    displayname = "MOD-ACTION"

    if "CLEARCHAT" in parts[1]:
        try:
            # Sets the message variable to the actual message sent
            username = parts[2][:len(parts[2]) - 1]
        except:
            username = ""
        # Sets the username variable to the actual username
        tags = str.split(parts[0], ';')


        # Mod action logging
        try:
            if "ban-duration" in tags[0]:
                reason = tags[1].split("=")[1].replace("\s", " ")
                duration = int(tags[0].split("=")[1])
                if duration <= 5:
                    message = f"purged: {username}. reason: {reason}"

                    insertoneindb("Modlog", {"action": "purged", "username": username, "duration": duration,
                                             "reason": reason, "timestamp": timestamp})
                    insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                              "sub": issub, "mod": ismod})
                    # if modroom_available:
                    #     s.send(
                    #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
                    #         channel_id.encode(), modroom_id.encode(), message.encode()))
                else:
                    message = f"Timed out: {username}. Duration: {duration}. Reason: {reason}"
                    insertoneindb("Modlog", {"action": "timed out", "username": username, "duration": duration,
                                             "reason": reason, "timestamp": timestamp})

                    insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                              "sub": issub, "mod": ismod})
                    # if modroom_available:
                    #     s.send(
                    #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
                    #         channel_id.encode(), modroom_id.encode(), message.encode()))

            elif username != "":
                reason = tags[0].split("=")[1].replace("/s", " ")
                message = f"Banned: {username}. Reason: {reason}"
                insertoneindb("Modlog", {"action": "banned", "username": username, "duration": 0,
                                         "reason": reason, "timestamp": timestamp})
                insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                          "sub": issub, "mod": ismod})
                # if modroom_available:
                #     s.send(
                #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
                #         channel_id.encode(), modroom_id.encode(), message.encode()))

        except Exception as errormsg:
            errorlog(errormsg, "Modlog", parts)
            raise errormsg
    elif "CLEARMSG" in parts[1]:
        try:
            tags = str.split(parts[0], ';')
            username = tags[0].split("=")[1]
            removedmessage = parts[2]
            message = f"Removed message from: {username}. Message: {removedmessage}"
            insertoneindb("Modlog", {"action": "message removed", "username": username, "message": message,
                                     "timestamp": timestamp})
            insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                      "sub": issub, "mod": ismod})
        except Exception as errormsg:
            errorlog(errormsg, "Modlog", parts)
            raise errormsg
