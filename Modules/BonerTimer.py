import random
import threading
import numbers
import os
import time

from Required.Sendmessage import send_message
from Required.Errorlog import errorlog
from datetime import datetime, date, timedelta
import Required.Database as Database
from Required.Logger import logtofile
from Required.APICalls import follows, usernametoid, idtousername


def load_bonertimer():
    global timeractive
    global betsopen
    global bets
    global timers
    global endings
    global titleholder
    timeractive = False
    betsopen = False
    bets = {}
    timers = {}
    endings = []

    for document in Database.getallfromdb("Endings"):
        endings.append(document["ending"])
    titleholder = Database.getonefromdb("Titleholder")["username"]


def announcer(userid, username, bettime):
    global bets; global timers
    try:
        try:
            ending = random.choice(endings)
        except:
            ending = ""
        send_message("%s's time has come with %s minutes! %s" % (username, bettime, ending))
        # bets.pop(displayname)
        timers.pop(userid)

    except Exception as errormsg:
        errorlog(errormsg, "BonerTimer/Announcer()", '')


def timer(message):
    global timeractive
    global betsopen
    global starttime
    global timers
    global bets
    arguments = message.split(" ")
    if arguments[1] == "start":
        if timeractive:
            send_message("Timer already started!")
        else:
            timeractive = True
            betsopen = False
            starttime = datetime.time(datetime.now())
            # Start all timer threads
            for t in list(timers.values()):
                t.start()
            send_message("The timer has been started. No more bets can be placed! "
                         "Good luck all!")
    elif arguments[1] == "stop":
        if timeractive:
            timeractive = False
            for t in list(timers.values()):
                t.cancel()
            timers = {}
            timenow = datetime.time(datetime.now())
            # Calculates the time since timer started
            timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                               starttime)
            # Crude way to add the hours to the total minute count
            endtime = str(timer).split(':')[1]
            if str(timer).split(':')[0] == '1':
                endtime += (int(endtime) + 60)
            if str(timer).split(':')[0] == '2':
                endtime += (int(endtime) + 120)
            # calculate the closest bet to the endtime
            winningtime = int(min(bets.values(), key=lambda x: abs(int(x) - int(endtime))))

            try:
                # check if winningtime is within 5 minutes of the endtime
                if (int(endtime) - 5) <= winningtime <= (int(endtime) + 5):
                    betval = list(bets.values())
                    # Check if there are more winners. Slightly different code if there are
                    # multiple peope with the same time
                    if betval.count(str(winningtime)) > 1:
                        winners = []
                        for i in list(bets.items()):
                            if i[1] == str(winningtime):
                                winners.append(i[0])
                        winner = " and ".join(winners)
                        send_message("Bones have been broken! The timer is on " +
                                     endtime + " minute(s)! The winners are: " + winner +
                                     " with " + str(winningtime) + " minutes!")
                    else:
                        winner = list(bets.keys())[list(bets.values()).index((str(winningtime)))]
                        # winner = min(list(bets.items()),
                        #              key=lambda __v: abs(int(__v[1]) - int(endtime)))
                        send_message("Bones have been broken! The timer is on " +
                                     endtime + " minute(s)! The winner is: " + winner +
                                     " with " + str(winningtime) + " minutes!")

                    Database.insertoneindb("Bonerwinners", {"name(s)": winner, "time": winningtime})
                    Database.insertoneindb("BonerTitleholder", {"name": winner})
                else:
                    send_message("Bones have been broken! The timer is on" + endtime + " minutes. No bets are within "
                                 "5 minutes of the timer. That means there is no winner this round!")

                # logtofile(folder, "Timer/stoptimer()", f"endtime: {str(endtime)}. Winning time: {str(winningtime)}")
            except Exception as errormsg:
                errorlog(errormsg, 'Bonertimer/stoptimer()', "")
        else:
            send_message("There is currently no timer active!")
    elif arguments[1] == "reset":
        try:
            timeractive = False
            betsopen = True
            for t in list(timers.values()):
                t.cancel()
            time.sleep(1)
            timers = {}
            send_message("Timer reset. Bets are now open again!")
        except Exception as errormsg:
            errorlog(errormsg, "BonerTimer/resettimer()", '')
    else:
        try:
            if timeractive:
                timenow = datetime.time(datetime.now())
                timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                                   starttime)
                timer = str(timer).split('.')[0]
                timersplit = timer.split(':')
                endtime = ":".join(timersplit)
                send_message("Fid has been alive for: " + endtime)
            else:
                send_message("There is currently no timer active!")
        except Exception as errormsg:
            errorlog(errormsg, "BonerTimer/timer()", '')


# def starttimer():
#     global timeractive; global betsopen; global starttime; global timers
#     if timeractive:
#         send_message("Timer already started!")
#     else:
#         timeractive = True
#         betsopen = False
#         starttime = datetime.time(datetime.now())
#         # Start all timer threads
#         for t in list(timers.values()):
#             t.start()
#         send_message("The timer has been started. No more bets can be placed! "
#                      "Good luck all!")


# def stoptimer():
#     global timeractive; global timers; global bets
#     if timeractive:
#         timeractive = False
#         for t in list(timers.values()):
#             t.cancel()
#         timers = {}
#         timenow = datetime.time(datetime.now())
#         # Calculates the time since timer started
#         timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
#                                                                            starttime)
#         # Crude way to add the hours to the total minute count
#         endtime = str(timer).split(':')[1]
#         if str(timer).split(':')[0] == '1':
#             endtime += (int(endtime) + 60)
#         if str(timer).split(':')[0] == '2':
#             endtime += (int(endtime) + 120)
#         # calculate the closest bet to the endtime
#         winningtime = int(min(bets.values(), key=lambda x: abs(int(x) - int(endtime))))
#
#         try:
#             # check if winningtime is within 5 minutes of the endtime
#             if (int(endtime) - 5) <= winningtime <= (int(endtime) + 5):
#                 betval = list(bets.values())
#                 # Check if there are more winners. Slightly different code if there are
#                 # multiple peope with the same time
#                 if betval.count(str(winningtime)) > 1:
#                     winners = []
#                     for i in list(bets.items()):
#                         if i[1] == str(winningtime):
#                             winners.append(i[0])
#                     winnerstr = " and ".join(winners)
#                     send_message("Bones have been broken! The timer is on " +
#                                  endtime + " minute(s)! The winners are: " + winnerstr +
#                                  " with " + str(winningtime) + " minutes!")
#                     with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevWinners.txt', 'a+') as f:
#                         for i in winners:
#                             f.write(i + ":" + str(winningtime) + "\n")
#                     with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
#                         f.write(winnerstr)
#                 else:
#                     winner = list(bets.keys())[list(bets.values()).index((str(winningtime)))]
#                     # winner = min(list(bets.items()),
#                     #              key=lambda __v: abs(int(__v[1]) - int(endtime)))
#                     send_message("Bones have been broken! The timer is on " +
#                                  endtime + " minute(s)! The winner is: " + winner +
#                                  " with " + str(winningtime) + " minutes!")
#                     with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevWinners.txt', 'a+') as f:
#                         f.write(winner + ":" + str(winningtime) + "\n")
#                     with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
#                         f.write(winner)
#             else:
#                 send_message("Bones have been broken! The timer is on " +
#                              endtime + " minutes. No bets are within 5 minutes of the "
#                                        "timer. That means there is no winner this round!")
#
#             print("endtime: " + endtime)
#             print("endtime - 5: " + str(int(endtime) - 5))
#             print("endtime + 5: " + str(int(endtime) + 5))
#             print("winning time: " + str(winningtime))
#         except Exception as errormsg:
#             Errorlog.errorlog(errormsg, 'Bonertimer/stoptimer()', "")
#         else:
#             with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevBets.txt', 'a+')as f:
#                 f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
#                         str(time.strftime("%X")) + "\n")
#                 f.write("Endtime: %s minutes\n" % endtime)
#                 for key in bets:
#                     f.write(key + ":" + str(bets[key]) + "\n")
#             bets = {}
#             with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
#                 f.write('')
#
#     else:
#         send_message("There is currently no timer active!")


# def timer():
#     try:
#         if timeractive:
#             timenow = datetime.time(datetime.now())
#             timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
#                                                                                starttime)
#             timer = str(timer).split('.')[0]
#             timersplit = timer.split(':')
#             endtime = ":".join(timersplit)
#             send_message("Fid has been alive for: " + endtime)
#         else:
#             send_message("There is currently no timer active!")
#     except Exception as errormsg:
#         Errorlog.errorlog(errormsg, "BonerTimer/timer()", '')


# def resettimer():
#     global timeractive; global betsopen; global timers
#     try:
#         timeractive = False
#         betsopen = True
#         for t in list(timers.values()):
#             t.cancel()
#         time.sleep(1)
#         timers = {}
#         send_message("Timer reset. Bets are now open again!")
#     except Exception as errormsg:
#         Errorlog.errorlog(errormsg, "BonerTimer/resettimer()", '')


def fidwins():
    global timeractive; global timers; global bets
    try:
        if timeractive:
            timeractive = False
            for t in list(timers.values()):
                t.cancel()
            time.sleep(1)
            timers = {}
            Database.updateoneindb("Titleholder", {}, {"username": "FideliasFK"}, True)
            timenow = datetime.time(datetime.now())
            timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                               starttime)
            endtime = str(timer).split(':')[1]
            if str(timer).split(':')[0] == '1':
                endtime += (int(endtime) + 60)
            if str(timer).split(':')[0] == '2':
                endtime += (int(endtime) + 120)
            send_message(f"The timer is on {endtime} minute(s)!")
            send_message("No boners have been broken this round. The winner is FideliasFK!")
        else:
            send_message("There is no timer active!")
    except Exception as errormsg:
        send_message("Error lettting fid win.")
        errorlog(errormsg, 'Bonertimer/fidwins', '')


def winner(message):
    global timeractive
    global timers
    global bets
    winner = message.split(" ")[1]
    try:
        if timeractive:
            timeractive = False
            for t in list(timers.values()):
                t.cancel()
            time.sleep(1)
            timers = {}
            Database.updateoneindb("Titleholder", {}, {"username": winner})
            send_message(f"The winner this round is {winner}!")
        else:
            send_message("There is no timer active!")
    except IndexError:
        send_message("Error setting new winner. Check your command.")
    except Exception as errormsg:
        send_message(f"There was an error setting {winner} as winner.")
        errorlog(errormsg, 'Bonertimer/winner()', message)
    else:
        Database.clearcollection("Bets")


def func_bets(message):
    global betsopen
    arguments = message.split(" ")
    if arguments[1] == "open":
        if not betsopen:
            betsopen = True
            send_message("Taking bets for the Broken Boner game! "
                         "Use !bet <number> to join in!")
        else:
            send_message("Bets already opened!")
    elif arguments[2] == "close":
        if betsopen:
            betsopen = False
            send_message("Bets are now closed!")
        else:
            send_message("Bets are already closed!")


def setboner(message):
    global titleholder
    arguments = message.split(" ")
    try:
        titleholder = arguments[1]
        Database.updateoneindb("Titleholder", {}, {"username": titleholder}, True)
        send_message("Registered " + titleholder + " as the new owner of \"Broken Boner\" ")
    except ValueError:
        send_message("Unable to determine new titleholder. Please check your command.")

    except Exception as errormsg:
        send_message("Error changing broken boner. Error logged.")
        errorlog(errormsg, 'Bonertimer/setboner()', message)


def currentboner():
    try:
        send_message("The current owner of the title \"Broken Boner\" is: " +
                     titleholder + "!")
    except Exception as errormsg:
        errorlog(errormsg, 'Bonertimer/currentboner()', '')
        send_message("Error reading current boner")


def brokenboner():
    send_message("The game is to bet how long it takes for Fid to break a leg or "
                 "die in ARMA. "
                 "The timer usually starts after the teleport pole or as the convoy moves out. "
                 "Anyone can join to try and win the title \"Broken Boner\"! "
                 "Use !bet <minutes> to place your bets!")


def betstats():
    if bets != {}:
        try:
            betvalues = [int(i) for i in list(bets.values())]
            lowest = min(betvalues)
            highest = max(betvalues)
            betsum = 0.0
            for key in bets:
                betsum += int(bets[key])
            length = len(bets)
            avg = round((betsum / len(bets)), 2)
            send_message(str(length) + " people are betting this round. The lowest bet is "
                         + str(lowest) + " minutes and the highest bet is "
                         + str(highest) + " minutes. The average is " + str(avg) +
                         " minutes.")
        except Exception as errormsg:
            errorlog(errormsg, 'Bonertimer/betstats', '')
            send_message("Error calculating numbers")
    else:
        send_message("No bets registered!")


def bet(username, userid, message, ismod):
    arguments = message.split(" ")
    global bets
    global timers
    if betsopen:
        if not ismod:
            followed_at = '2010-01-01T22:33:44Z'
        else:
            bet_tempvar1 = follows(userid)["followed_at"]
            if bet_tempvar1 != {}:
                followed_at = bet_tempvar1
            else:
                followed_at = datetime.now()

        followed_at = datetime.strptime(followed_at, '%Y-%m-%dT%H:%M:%SZ')
        if datetime.now() - followed_at >= timedelta(days=7):
            try:
                bet = arguments[1]
                if isinstance(int(bet), numbers.Number):
                    if int(bet) <= 0:
                        send_message("Please don't try to invoke the apocalypse. Thanks.")
                    elif userid in bets.keys():
                        bets[userid] = bet
                        betsec = int(bet) * 60
                        t = threading.Timer(betsec, announcer, [userid, username, bet])
                        timers[username] = t
                        Database.updateoneindb("Bets", {"userid": userid}, {"bet": bet}, True)
                        send_message(f"@{username} Bet updated! Your new bet is: {bet} minutes!")
                    else:
                        bets[userid] = bet
                        betsec = int(bet) * 60
                        t = threading.Timer(betsec, announcer, [username, bet])
                        timers[username] = t
                        Database.updateoneindb("Bets", {"userid": userid}, {"bet": bet}, True)
                        send_message(f"@{username} Bet registered: {bet} minutes!")
                else:
                    send_message("Bet is not a number")
            except ValueError as e:
                if str(e) == 'substring not found':
                    send_message("Use !bet <number> to enter the competition!")
                else:
                    send_message(f"{bet} is not a valid bet. Please use whole numbers only.")
            except Exception as errormsg:
                errorlog(errormsg, 'Bonertimer/bet()', message)
                send_message("There was an error registering your bet. Please try again.")
        else:
            send_message("This is a community game. You most be following for at least 7 days before you can join!")
    else:
        send_message("Bets are not currently opened.")


def addbet(message):
    global bets
    global timers
    try:
        arguments = message.split(' ')
        username = arguments[1]
        bet = arguments[2]
        userid = usernametoid(username)

        bets[userid] = bet
        t = threading.Timer((int(bet) * 60), announcer, [username, bet])
        timers[username] = t
        Database.updateoneindb("Bets", {"userid": userid}, {"bet": bet}, True)
        send_message(f"Bet for {username} with {bet} minutes added to pool!")
    except Exception as errormsg:
        send_message("Error adding bet for this user.")
        errorlog(errormsg, 'Bonertimer/addbet()', message)


def removebet(message):
    global bets
    global timers
    try:
        rembet = message.split(" ")[1]
        if all(i.isdigit() for i in rembet):
            if int(rembet) in list(bets.values()):
                if list(bets.values()).count(int(rembet)) > 1:
                    users = []
                    index = 0
                    for i in list(bets.values()):
                        if int(rembet) == i:
                            users.append(list(bets.keys())[index])
                        index += 1
                    send_message(f"Found more than one bet of {rembet} by these users: {str(users)}")

                else:
                    userid = list(bets.keys())[list(bets.values()).index(int(rembet))]
                    username = idtousername(userid)
                    del bets[userid]
                    del timers[username]
                    send_message(f"Bet for {username} removed from pool.")
            else:
                raise Exception
        else:
            if rembet in list(bets.keys()):
                userid = usernametoid(rembet)

                del bets[userid]
                del timers[rembet]
                Database.deleteoneindb("Bets", {"userid": userid})
                send_message(f"Bet for {rembet} removed from pool")
            else:
                raise Exception
    except Exception as errormsg:
        send_message("Error removing user from current pool.")
        errorlog(errormsg, 'Bonertimer/removebet()', message)


def clearbets():
    global bets
    global timers
    try:
        bets = {}
        timers = {}
        send_message("Bets cleared!")
        Database.clearcollection("Bets")
    except Exception as errormsg:
        send_message("Error clearing the bets. Error logged.")
        errorlog(errormsg, 'Bonertimer/clearbets()', '')


def mybet(username, userid):
    try:
        if bets.get(userid):
            send_message(username + " your bet is: " +
                         str(bets.get(userid)) + " minutes!")
        else:
            send_message("No bet registered!")
    except Exception as errormsg:
        send_message("There was an error showing your bet!")
        errorlog(errormsg, 'Bonertimer/mybet()', "Username: " + username)
