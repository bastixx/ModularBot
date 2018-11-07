import os
import requests
import random
from datetime import datetime, timedelta

from Errorlog import errorlog
from Send_message import send_message


def load_raffles(FOLDER, CLIENTID, CHANNELID):
    global raffles; global rafflewinners; global folder; global client_id; global channel_id
    raffles = {}
    rafflelist = []
    rafflewinners = {}
    folder = FOLDER
    client_id = CLIENTID
    channel_id = CHANNELID

    if not os.path.isdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle'):
        os.mkdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle')

    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt') as f:
            for line in f:
                key = line.strip("\n")
                rafflelist.append(key)

        for i in rafflelist:
            raffles[i] = []
            rafflewinners[i] = []
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{i}.txt', "r") as f:
                for line in f:
                    if raffles[i]:
                        raffles[i].append(line.strip("\n"))
                    else:
                        raffles[i] = [line.strip("\n")]
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{i}winners.txt', "r") as f:
                for line in f:
                    if rafflewinners[i]:
                        rafflewinners[i].append(line.strip("\n"))
                    else:
                        rafflewinners[i] = [line.strip("\n")]
    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', 'w'):
            pass


def raffle(s, message):
    global raffles; global rafflewinners
    try:
        arguments = message.split(" ")
        raffle = " ".join(arguments[2:])
        if arguments[1] == "add":
            try:
                raffles[raffle] = []
                rafflewinners[raffle] = []
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}.txt', 'w'):
                    pass
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}winners.txt', 'w'):
                    pass
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', "a") as f:
                    f.write("%s\n" % raffle)
                send_message(s, "Raffle \"%s\" created!" % raffle)
            except:
                send_message(s, "Error creating raffle!")
        elif arguments[1] == "remove":
            try:
                del raffles[raffle]
                os.remove(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}.txt')
                os.remove(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}winners.txt')
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', "w") as f:
                    for i in raffles.keys():
                        f.write("%s\n" % i)
                send_message(s, "Raffle \"%s\" deleted!" % raffle)
            except Exception as e:
                send_message(s, "Error removing raffle!")
                print(e)
        elif arguments[1] == "list":
            send_message(s, "Current raffles are: %s." % ", ".join(raffles.keys()))
            print(raffles)
        elif arguments[1] == "roll":
            if len(raffles[raffle]) == 0:
                send_message(s, "No contestants left!")
            else:
                rafflewinner = random.choice(raffles[raffle])
                raffles[raffle].remove(rafflewinner)
                rafflewinners[raffle].append(rafflewinner)

                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt" % raffle, 'w') as f:
                    for i in raffles[raffle]:
                        f.write("%s\n" % i)
                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%swinners.txt" % raffle, 'a') as f:
                    f.write("%s\n" % rafflewinner)
                send_message(s, "The winner is: %s!" % rafflewinner)
        elif arguments[1] == "adduser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user not in raffles[raffle]:
                if user not in rafflewinners[raffle]:
                    raffles[raffle].append(user)
                    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt' % raffle, 'a') as f:
                        f.write("%s\n" % user)
                    send_message(s,
                                 "@%s joined raffle: \"%s\"!" % (user, raffle))
                else:
                    send_message(s, "user @%s already won this raffle!" % user)
            else:
                send_message(s, "User @%s is already in this raffle!" % user)
        elif arguments[1] == "removeuser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user in raffles[raffle]:
                raffles[raffle].remove(user)
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt' % raffle, 'w') as f:
                    for i in raffles[raffle]:
                        f.write("%s\n" % i)
                send_message(s, "@%s removed from raffle: \"%s\"!" % (user, raffle))
            else:
                send_message(s, "User @%s is not in this raffle!" % user)
        elif arguments[1] == "resetwinners":
            raffle = " ".join(arguments[2:])
            if raffle in rafflewinners.keys():
                rafflewinners[raffle] = []
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%swinners.txt' % raffle, 'w') as f:
                    f.write("")
                send_message(s, "Rafflewinners \"%s\" cleared!" % raffle)
            else:
                send_message(s, f"Raffle {raffle} has no winners or does not exist.")
        elif arguments[1] == "stats":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                send_message(s, f"The current number of people in this raffle are: {len(raffles[raffle])}")

    except IndexError:
        send_message(s, "To join a raffle, use !join <raffle name>. Current raffles are: "
                        "%s" % ", ".join(raffles.keys()))

    except Exception as errormsg:
        errorlog(errormsg, "!raffle", message)


def join_raffle(s, displayname, message, ismod):
    global raffles
    arguments = message.split(" ")
    raffle = " ".join(arguments[1:])

    try:
        url = 'https://api.twitch.tv/helix/users?login=%s' % displayname
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        userid = r["data"][0]['id']

        if ismod:
            followed_at = '2010-01-01T22:33:44Z'
        else:
            url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channel_id)
            headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            followed_at = r["data"][0]['followed_at']

        followed_at_formatted = datetime.strptime(followed_at, '%Y-%m-%dT%H:%M:%SZ')
        time_now = datetime.now()

        if time_now - followed_at_formatted >= timedelta(days=7):
            try:
                if displayname not in raffles[raffle]:
                    if displayname not in rafflewinners[raffle]:
                        raffles[raffle].append(displayname)
                        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt" % raffle, 'a') as f:
                            f.write("%s\n" % displayname)
                        send_message(s, "@%s joined raffle: \"%s\"!" % (displayname, raffle))
                    else:
                        send_message(s, "@%s you already won this raffle!" % displayname)
                else:
                    send_message(s, "@%s you are already in this raffle!" % displayname)
            except IndexError:
                send_message(s, "To join a raffle, use !join <raffle name>. Current raffles are: "
                                "%s" % ", ".join(raffles.keys()))
            except Exception:
                send_message(s, "Error adding user %s to raffle: \"%s\". Check if you spelled the "
                             "raffle name correctly." % (displayname, raffle))
        else:
            send_message(s, "You have to be following this channel for at least 7 days before"
                         " you can join this raffle.")
    except IndexError:
        send_message(s, "You have to be following this channel for at least 7 days before"
                     " you can join this raffle.")

    except Exception as errormsg:
        errorlog(errormsg, "Raffles/join()", message)
