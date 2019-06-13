import random
from datetime import datetime, timedelta
import logging

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database
from Modules.Required.APICalls import username_to_id, follows

logger = logging.getLogger(__name__)


def load_raffles():
    global raffles
    raffles = {}
    try:
        if Database.collectionexists("Raffles"):
            for document in Database.getall("Raffles"):
                raffles[document["rafflename"]] = {"mode": document["mode"], "raffleentries": {}, "rafflewinners": {},
                                                   "silent": document["silent"]}
        for i in raffles.keys():
            for document in Database.getall("raffle_" + i):
                raffles[i]["raffleentries"][document["userid"]] = document["username"]
                if document["haswon"]:
                    raffles[i]["rafflewinners"][document["userid"]] = document["username"]
    except:
        logger.exception('')
        return False


def func_raffle(message):
    global raffles
    try:
        # !raffle (add|list|etc..) (username) raffle name
        arguments = message.split(" ")
        raffle = " ".join(arguments[2:])
        if arguments[1] == "add":
            try:
                raffles[raffle] = {"mode": "all", "raffleentries": {}, "rafflewinners": {}, "silent": False}
                Database.insertone("Raffles", {"rafflename": raffle, "mode": "all"})
                send_message(f"Raffle \"{raffle}\" created!")
            except:
                logger.exception(f'message: {message}')
                send_message(f"Error creating raffle \"{raffle}\"!")

        elif arguments[1] == "remove":
            try:
                if raffle in raffles.keys():
                    del raffles[raffle]
                    # TODO update database stuff
                    Database.deletecollection("raffle_" + raffle)
                    Database.deleteone("Raffles", {"rafflename": raffle})
                    send_message(f"Raffle \"{raffle}\" deleted!")
                else:
                    send_message("This raffle does not exist!")
            except:
                logger.exception(f'message: {message}')
                send_message("Error removing raffle!")

        elif arguments[1] == "get":
            # !raffle get mode|silent raffle
            raffle = " ".join(arguments[3:])
            try:
                if raffle in raffles.keys():
                    if arguments[2] == "mode":
                        send_message(f"Current mode for raffle {raffle} is: {raffles[raffle]['mode']}.")
                    elif arguments[2] == "silent":
                        if raffles[raffle]['mode']:
                            send_message(f"Silent mode for raffle {raffle} is enabled.")
                        else:
                            send_message(f"Silent mode for raffle {raffle} is disabled.")
                    else:
                        send_message("For the option \"get\" the allowed arguments are: \"mode\" and \"silent\".")
            except:
                logger.exception(f'message: {message}')
                send_message("Error changing mode for this raffle.")

        elif arguments[1] == "set":
            # !raffle set mode raffle
            try:
                if arguments[2] == "mode":
                    if arguments[3] in ['sub', 'follower', 'follower_7', 'all']:
                        mode = arguments[3]
                        raffle = " ".join(arguments[4:])
                        raffles[raffle]["mode"] = mode
                        Database.updateone("Raffles", {"rafflename": raffle}, {"mode": mode})
                        send_message(f"Mode changed for raffle {raffle}.")
                    else:
                        send_message("Correct modes are: sub, follower, follower_7 and all")
                elif arguments[2] == "silent":
                    newmode = arguments[3]
                    raffle = " ".join(arguments[4:])
                    if raffle in raffles.keys():
                        if newmode == "on":
                            raffles[raffle]["silent"] = True
                            send_message(f"Silent mode enabled for raffle {raffle}.")
                        elif newmode == "off":
                            raffles[raffle]["silent"] = False
                            send_message(f"Silent mode disabled for raffle {raffle}.")
                        else:
                            send_message("For the option \"silent\" the allowed arguments are: \"on\" and \"off\".")
                else:
                    send_message("For the option \"set\" the allowed arguments are: \"mode\" and \"silent\".")
            except:
                logger.exception(f'message: {message}')
                send_message("Error changing mode for this raffle.")

        elif arguments[1] == "list":
            if len(raffles > 0):
                send_message(f"Current raffles are: {", ".join(raffles.keys())}.")
            else:
                send_message("There are currently no raffles going.")

        # Command to roll a winner for a raffle. Mod only
        elif arguments[1] == "roll":
            try:
                if len(raffles[raffle]["raffleentries"]) == 0:
                    send_message("No contestants left!")
                else:
                    rafflewinnerid = random.choice(raffles[raffle]["raffleentries"].keys())
                    rafflewinnername = raffles[raffle]["raffleentries"][rafflewinnerid]
                    raffles[raffle]["raffleentries"].pop(rafflewinnerid)
                    raffles[raffle]["rafflewinners"][rafflewinnerid] = rafflewinnername

                    Database.updateone("raffle_" + raffle, {"userid": rafflewinnerid}, {"haswon": True})
                    send_message(f"The winner is: {rafflewinnername}!")
            except:
                logger.exception(f'message: {message}')
                send_message("Error rolling a winner for this raffle.")

        # Command to add a user to an raffle. Mod only.
        elif arguments[1] == "adduser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])
            userid = username_to_id(user)

            if userid not in raffles[raffle]["raffleentries"].keys():
                if user not in raffles[raffle]["rafflewinners"].keys():
                    raffles[raffle]["raffleentries"][userid] = user
                    Database.insertone("raffle_" + raffle, {"userid": userid, "username": user, "haswon": False})
                    send_message(f"@{user} joined raffle: \"{raffle}\"!")
                else:
                    send_message(f"user @{user} already won this raffle!")
            else:
                send_message(f"User @{user} is already in this raffle!")
                
        # Command to remove a user from a raffle. Mod only.
        elif arguments[1] == "removeuser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])
            userid = username_to_id(user)
            
            if userid in raffles[raffle]["raffleentries"].keys():
                raffles[raffle]["raffleentries"].pop(userid)
                Database.deleteone("raffle_" + raffle, {"userid": userid})
                send_message(f"@{user} removed from raffle: \"{raffle}\"!")
            else:
                send_message(f"User @{user} is not in this raffle!")
                
        # Command to clear the winners list, allowing everyone to enter and win again. Mod only.
        elif arguments[1] == "resetwinners":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                raffles[raffle]["Rafflewinners"] = {}

                Database.updatemany("raffle_" + raffle, {"haswon": True}, {"haswon": False})
                send_message(f"All winners for raffle \"{raffle}\" have been reset. " 
                             "Everyone who entered is still in the raffle.")
            else:
                send_message(f"Raffle \"{raffle}\" has no winners or does not exist.")
        elif arguments[1] == "stats":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                send_message(f"There are currently {len(raffles[raffle]["raffleentries"])} people in this raffle.")

        elif arguments[1] == "mode":
            send_message(f"The mode for raffle \"{raffle}\" is: {raffles[raffle]["mode"]}")

        else:
            send_message("Unknown command. Please check your message and try again.")

    except IndexError:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))
    except:
        logger.exception(f'message: {message}')
        send_message("There was an unexpected error. Please check your command and try again.")


def join_raffle(userid, username: str, message: str, issub: bool, ismod: bool) -> None:
    global raffles
    allowed = False
    arguments = message.split(" ")
    raffle = " ".join(arguments[1:])

    time_now = datetime.now()
    try:
        if ismod:
            followed_at = '2010-01-01T22:33:44Z'
        else:
            followed_at = follows(userid)['followed_at']
        followed_at_formatted = datetime.strptime(followed_at, '%Y-%m-%dT%H:%M:%SZ')

        following = True
    except IndexError:
        following = False
    except:
        following = False
        logger.exception(f'message: {message}')

    try:
        mode = raffles[raffle]["mode"]
    except:
        send_message(f"To join a raffle, use !join <raffle name>. Current raffles are: {", ".join(raffles.keys())}")
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
            if userid not in raffles[raffle]["raffleentries"].keys():
                if userid not in raffles[raffle]["Rafflewinners"].keys():
                    raffles[raffle]["raffleentries"][userid] = username
                    Database.insertone("raffle_" + raffle, {"userid": userid, "username": username,
                                                                "haswon": False})
                    if not raffles[raffle]['silent']:
                        send_message(f"@{username} joined raffle: \"{raffle}\"!")
                else:
                    send_messagef(f"@{username} you already won this raffle!")
            else:
                send_message(f"@{username} you are already in this raffle!")
        except IndexError:
                send_message(f"To join a raffle, use !join <raffle name>. Current raffles are: {", ".join(raffles.keys())}")

        except:
            logger.exception(f'message: {message}')
            send_message(f"Error adding user {username} to raffle: \"{raffle}\". Check if you spelled the "
                         "raffle name correctly.")

    else:
        if mode == 'sub':
            send_message("This raffle is for subscribers only.")
        elif mode == 'follower':
            send_message("You have to be following this channel to join this raffle.")
        elif mode == 'follower_7':
            send_message("You have to be following this channel for at least 7 days to join this raffle.")
