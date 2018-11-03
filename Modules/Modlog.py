import requests
import time
import os

from Errorlog import errorlog


# Try and get the ID for the mod channel. This is used for the moderation log.
def load_modlog(CHANNEL_ID, headers, FOLDER):
    global modroom_available; global modroom_id; global channel_id; global folder
    channel_id = CHANNEL_ID
    folder = FOLDER
    try:
        url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
        r = requests.get(url, headers=headers).json()
        modroom_id = r['rooms'][0]['_id']
        modroom_available = True
    except:
        modroom_available = False

    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Modlog.txt', 'w'):
        pass
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y")
              + ".txt", 'w'):
        pass


def modlog(s, parts):
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
            duration = tags[0].split("=")[1]
            if int(duration) <= 5:
                message = f"PURGED| Username: {username}\n"
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Modlog.txt', 'a') as f:
                    f.write(message)
                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y") + ".txt", 'a+') as f:
                    f.write(message)
                if modroom_available:
                    s.send(
                        b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (channel_id.encode(), modroom_id.encode(), message.encode()))
            else:
                message = f"TIMED OUT| Username: {username} | Reason: \"{reason}\" | Duration: {duration}\n"
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Modlog.txt', 'a') as f:
                    f.write(message)
                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y") + ".txt", 'a+') as f:
                    f.write(message)
                if modroom_available:
                    s.send(
                        b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (channel_id.encode(), modroom_id.encode(), message.encode()))

        elif username != "":
            reason = tags[0].split("=")[1].replace("/s", " ")
            message = f"BANNED| Username: {username} | Reason: {reason} \n"
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Modlog.txt', 'a') as f:
                f.write(message)
            with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/chatlogs/" + time.strftime("%d-%m-%Y") + ".txt", 'a+') as f:
                f.write(message)
            if modroom_available:
                s.send(b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (channel_id.encode(), modroom_id.encode(), message.encode()))

    except Exception as errormsg:
        errorlog(errormsg, "Modlog", parts)
        raise errormsg