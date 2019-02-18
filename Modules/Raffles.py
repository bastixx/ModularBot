import os
import requests
import random
from datetime import datetime, timedelta

from Errorlog import errorlog
from Sendmessage import send_message


def load_raffles(FOLDER, CLIENTID, CHANNELID):
    global raffles
    global rafflewinners
    global rafflelist
    global folder
    global client_id
    global channel_id
    raffles = {}
    rafflelist = {}
    rafflewinners = {}
    folder = FOLDER
    client_id = CLIENTID
    channel_id = CHANNELID

    if not os.path.isdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle'):
        os.mkdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle')

    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt') as f:
            for line in f:
                line = line.strip("\n")
                key, mode = line.split(":")
                rafflelist[key] = mode

        for i in rafflelist.keys():
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
    global raffles
    global rafflewinners
    try:
        arguments = message.split(" ")
        raffle = " ".join(arguments[2:])
        if arguments[1] == "add":
            try:
                mode = 'all'
                raffles[raffle] = []
                rafflewinners[raffle] = []
                rafflelist[raffle] = mode
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}.txt', 'w'):
                    pass
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}winners.txt',
                          'w'):
                    pass
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', "a") as f:
                    f.write(f"{raffle}:{mode}\n")
                send_message("Raffle \"%s\" created!" % raffle)
            except:
                send_message("Error creating raffle!")
        elif arguments[1] == "remove":
            try:
                del raffles[raffle]
                os.remove(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}.txt')
                os.remove(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/{raffle}winners.txt')
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', "w") as f:
                    for i in raffles.keys():
                        f.write("%s\n" % i)
                send_message("Raffle \"%s\" deleted!" % raffle)
            except Exception as e:
                send_message("Error removing raffle!")
                print(e)
        elif arguments[1] == "set":
            # !raffle set mode raffle
            try:
                if arguments[2] in ['sub', 'follower', 'follower_7', 'all']:
                    mode = arguments[2]
                    raffle = " ".join(arguments[3:])
                    rafflelist[raffle] = mode
                    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/Raffles.txt', "w") \
                            as f:
                        for key in rafflelist.keys():
                            f.write(f"{key}:{rafflelist[key]}\n")

                    send_message(f"Mode changed for raffle {raffle}.")
                else:
                    send_message("Correct modes are: sub, follower, follower_7 and all")
            except Exception as errormsg:
                send_message("Error changing mode for this raffle.")
                errorlog(errormsg, "Raffle/set()", message)

        elif arguments[1] == "list":
            send_message("Current raffles are: %s." % ", ".join(raffles.keys()))
            print(raffles)
        elif arguments[1] == "roll":
            if len(raffles[raffle]) == 0:
                send_message("No contestants left!")
            else:
                rafflewinner = random.choice(raffles[raffle])
                raffles[raffle].remove(rafflewinner)
                rafflewinners[raffle].append(rafflewinner)

                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt" % raffle,
                          'w') as f:
                    for i in raffles[raffle]:
                        f.write("%s\n" % i)
                with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%swinners.txt" % raffle,
                          'a') as f:
                    f.write("%s\n" % rafflewinner)
                send_message("The winner is: %s!" % rafflewinner)
        elif arguments[1] == "adduser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user not in raffles[raffle]:
                if user not in rafflewinners[raffle]:
                    raffles[raffle].append(user)
                    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt' % raffle,
                              'a') as f:
                        f.write("%s\n" % user)
                    send_message("@%s joined raffle: \"%s\"!" % (user, raffle))
                else:
                    send_message("user @%s already won this raffle!" % user)
            else:
                send_message("User @%s is already in this raffle!" % user)
        elif arguments[1] == "removeuser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user in raffles[raffle]:
                raffles[raffle].remove(user)
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt' % raffle,
                          'w') as f:
                    for i in raffles[raffle]:
                        f.write("%s\n" % i)
                send_message("@%s removed from raffle: \"%s\"!" % (user, raffle))
            else:
                send_message("User @%s is not in this raffle!" % user)
        elif arguments[1] == "resetwinners":
            raffle = " ".join(arguments[2:])
            if raffle in rafflewinners.keys():
                rafflewinners[raffle] = []
                with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%swinners.txt' % raffle,
                          'w') as f:
                    f.write("")
                send_message("Rafflewinners \"%s\" cleared!" % raffle)
            else:
                send_message(f"Raffle {raffle} has no winners or does not exist.")
        elif arguments[1] == "stats":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                send_message(f"There are currently {len(raffles[raffle])} people in this raffle.")

        elif arguments[1] == "mode":
            send_message(f"{rafflelist[raffle]}")

    except IndexError:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))

    except Exception as errormsg:
        errorlog(errormsg, "!raffle", message)


def join_raffle(s, displayname, message, issub, ismod):
    global raffles
    allowed = False
    arguments = message.split(" ")
    raffle = " ".join(arguments[1:])

    time_now = datetime.now()
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

        following = True
    except IndexError:
        following = False
    except Exception as errormsg:
        following = False
        errorlog(errormsg, "Raffles/join()", message)


    try:
        mode = rafflelist[raffle]
    except:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))
        return

    if mode == "sub" and issub:
        allowed = True
    elif mode == "follower" and following:
        allowed = True
    elif mode == "follower_7" and following:
        if time_now - followed_at_formatted >= timedelta(days=7):
            allowed = True
    elif mode == "all":
        allowed = True
    else:
        allowed = False

    if allowed:
        try:
            if displayname not in raffles[raffle]:
                if displayname not in rafflewinners[raffle]:
                    raffles[raffle].append(displayname)
                    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/raffle/%s.txt" % raffle,
                              'a') as f:
                        f.write("%s\n" % displayname)
                    send_message("@%s joined raffle: \"%s\"!" % (displayname, raffle))
                else:
                    send_message("@%s you already won this raffle!" % displayname)
            else:
                send_message("@%s you are already in this raffle!" % displayname)
        except IndexError:
            send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                         "%s" % ", ".join(raffles.keys()))
        except Exception:
            send_message("Error adding user %s to raffle: \"%s\". Check if you spelled the "
                         "raffle name correctly." % (displayname, raffle))
    else:
        if mode == 'sub':
            send_message("This raffle is for subscribers only.")
        elif mode == 'follower':
            send_message("You have to be following this channel to join this raffle.")
        elif mode == 'follower_7':
            send_message("You have to be following this channel for at least 7 days to join this raffle")
