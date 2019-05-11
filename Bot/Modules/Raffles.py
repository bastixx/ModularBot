import random
from datetime import datetime, timedelta

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database
from Modules.Required.APICalls import username_to_id, follows


def load_raffles():
    global raffles
    raffles = {}
    try:
        if Database.collectionexists("Raffles"):
            for document in Database.getallfromdb("Raffles"):
                raffles[document["rafflename"]] = {"mode": document["mode"], "raffleentries": {}, "rafflewinners": {},
                                                   "silent": document["silent"]}
        for i in raffles.keys():
            for document in Database.getallfromdb("raffle_" + i):
                raffles[i]["raffleentries"][document["userid"]] = document["username"]
                if document["haswon"]:
                    raffles[i]["rafflewinners"][document["userid"]] = document["username"]

    except Exception as errormsg:
        errorlog(errormsg, "Raffles/Load_raffles()", "")


def func_raffle(message):
    global raffles
    try:
        # !raffle (add|list|etc..) (username) raffle name
        arguments = message.split(" ")
        raffle = " ".join(arguments[2:])
        if arguments[1] == "add":
            try:
                raffles[raffle] = {"mode": "all", "raffleentries": {}, "rafflewinners": {}, "silent": False}
                Database.insertoneindb("Raffles", {"rafflename": raffle, "mode": "all"})
                send_message("Raffle \"%s\" created!" % raffle)
            except Exception as errormsg:
                send_message(f"Error creating raffle \"%s\"!" % raffle)
                errorlog(errormsg, "Func_raffle/add()", message)

        elif arguments[1] == "remove":
            try:
                if raffle in raffles.keys():
                    del raffles[raffle]
                    Database.deletecollection("raffle_" + raffle)
                    Database.deleteoneindb("Raffles", {"rafflename": raffle})
                    send_message("Raffle \"%s\" deleted!" % raffle)
                else:
                    send_message("This raffle does not exist!")
            except Exception as errormsg:
                send_message("Error removing raffle!")
                errorlog(errormsg, "Func_raffle/remove()", message)

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
            except Exception as errormsg:
                send_message("Error changing mode for this raffle.")
                errorlog(errormsg, "Func_raffle/get()", message)

        elif arguments[1] == "set":
            # !raffle set mode raffle
            try:
                if arguments[2] == "mode":
                    if arguments[3] in ['sub', 'follower', 'follower_7', 'all']:
                        mode = arguments[3]
                        raffle = " ".join(arguments[4:])
                        raffles[raffle]["mode"] = mode
                        Database.updateoneindb("Raffles", {"rafflename": raffle}, {"mode": mode})
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
            except Exception as errormsg:
                send_message("Error changing mode for this raffle.")
                errorlog(errormsg, "Func_raffle/set()", message)

        elif arguments[1] == "list":
            if len(raffles > 0):
                send_message("Current raffles are: %s." % ", ".join(raffles.keys()))
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

                    Database.updateoneindb("raffle_" + raffle, {"userid": rafflewinnerid}, {"haswon": True})
                    send_message("The winner is: %s!" % rafflewinnername)
            except Exception as errormsg:
                send_message("Error rolling a winner for this raffle.")
                errorlog(errormsg, "Func_raffle/roll()", message)

        # Command to add a user to an raffle. Mod only.
        elif arguments[1] == "adduser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])
            userid = username_to_id(user)

            if userid not in raffles[raffle]["raffleentries"].keys():
                if user not in raffles[raffle]["rafflewinners"].keys():
                    raffles[raffle]["raffleentries"][userid] = user
                    Database.insertoneindb("raffle_" + raffle, {"userid": userid, "username": user, "haswon": False})
                    send_message("@%s joined raffle: \"%s\"!" % (user, raffle))
                else:
                    send_message("user @%s already won this raffle!" % user)
            else:
                send_message("User @%s is already in this raffle!" % user)
                
        # Command to remove a user from a raffle. Mod only.
        elif arguments[1] == "removeuser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])
            userid = username_to_id(user)
            
            if userid in raffles[raffle]["raffleentries"].keys():
                raffles[raffle]["raffleentries"].pop(userid)
                Database.deleteoneindb("raffle_" + raffle, {"userid": userid})
                send_message("@%s removed from raffle: \"%s\"!" % (user, raffle))
            else:
                send_message("User @%s is not in this raffle!" % user)
                
        # Command to clear the winners list, allowing everyone to enter and win again. Mod only.
        elif arguments[1] == "resetwinners":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                raffles[raffle]["Rafflewinners"] = {}

                Database.updatemanyindb("raffle_" + raffle, {"haswon": True}, {"haswon": False})
                send_message("All winners for raffle \"%s\" have been reset. " 
                             "Everyone who entered is still in the raffle." % raffle)
            else:
                send_message("Raffle \"%s\" has no winners or does not exist." % raffle)
        elif arguments[1] == "stats":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                send_message("There are currently \"%s\" people in this raffle." % len(raffles[raffle]["raffleentries"]))

        elif arguments[1] == "mode":
            send_message("The mode for raffle \"%s\" is: %s" % (raffle, raffles[raffle]["mode"]))

        else:
            send_message("Unknown command. Please check your message and try again.")

    except IndexError:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))

    except Exception as errormsg:
        errorlog(errormsg, "!raffle", message)
        send_message("There was an unexpected error. Please check your comamnd and try again.")


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
    except Exception as errormsg:
        following = False
        errorlog(errormsg, "Raffles/join()", message)

    try:
        mode = raffles[raffle]["mode"]
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
            if userid not in raffles[raffle]["raffleentries"].keys():
                if userid not in raffles[raffle]["Rafflewinners"].keys():
                    raffles[raffle]["raffleentries"][userid] = username
                    Database.insertoneindb("raffle_" + raffle, {"userid": userid, "username": username,
                                                                "haswon": False})
                    if not raffles[raffle]['silent']:
                        send_message("@%s joined raffle: \"%s\"!" % (username, raffle))
                else:
                    send_message("@%s you already won this raffle!" % username)
            else:
                send_message("@%s you are already in this raffle!" % username)
        except IndexError:
            send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                         "%s" % ", ".join(raffles.keys()))
        except Exception as errormsg:
            send_message("Error adding user %s to raffle: \"%s\". Check if you spelled the "
                         "raffle name correctly." % (username, raffle))
            errorlog(errormsg, "Raffles/join()", message)

    else:
        if mode == 'sub':
            send_message("This raffle is for subscribers only.")
        elif mode == 'follower':
            send_message("You have to be following this channel to join this raffle.")
        elif mode == 'follower_7':
            send_message("You have to be following this channel for at least 7 days to join this raffle.")
