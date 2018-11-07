import random
import threading
import numbers
import os
import time

from Send_message import send_message
from Errorlog import errorlog
from datetime import datetime, date


def load_bonertimer(FOLDER):
    global folder; global timeractive; global betsopen; global bets; global timers; global endings
    timeractive = False
    betsopen = False
    folder = FOLDER
    bets = {}
    timers = {}
    endings = []

    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Endings.txt', 'w') as f:
            endings = f.readlines()
            endings = [x.strip('\n') for x in endings]
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "r"):
            pass

    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Endings.txt', 'w'):
            pass
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt', 'w') as f:
            f.write("No titleholder yet")


def announcer(s, displayname, bettime):
    global bets; global timers
    try:
        try:
            ending = random.choice(endings)
        except:
            ending = ""
        send_message(s, "%s's time has come with %s minutes! %s" % (displayname, bettime, ending))
        # bets.pop(displayname)
        timers.pop(displayname)

    except Exception as errormsg:
        errorlog(errormsg, "Announcer()", '')


def starttimer(s):
    global timeractive; global betsopen; global starttime; global timers
    if timeractive:
        send_message(s, "Timer already started!")
    else:
        timeractive = True
        betsopen = False
        starttime = datetime.time(datetime.now())
        # Start all timer threads
        for t in list(timers.values()):
            t.start()
        send_message(s, "The timer has been started. No more bets can be placed! "
                     "Good luck all!")


def stoptimer(s):
    global timeractive; global timers; global bets
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
                    winnerstr = " and ".join(winners)
                    send_message(s, "Bones have been broken! The timer is on " +
                                 endtime + " minute(s)! The winners are: " + winnerstr +
                                 " with " + str(winningtime) + " minutes!")
                    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevWinners.txt', 'a+') as f:
                        for i in winners:
                            f.write(i + ":" + str(winningtime) + "\n")
                    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
                        f.write(winnerstr)
                else:
                    winner = list(bets.keys())[list(bets.values()).index((str(winningtime)))]
                    # winner = min(list(bets.items()),
                    #              key=lambda __v: abs(int(__v[1]) - int(endtime)))
                    send_message(s, "Bones have been broken! The timer is on " +
                                 endtime + " minute(s)! The winner is: " + winner +
                                 " with " + str(winningtime) + " minutes!")
                    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevWinners.txt', 'a+') as f:
                        f.write(winner + ":" + str(winningtime) + "\n")
                    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
                        f.write(winner)
            else:
                send_message(s, "Bones have been broken! The timer is on " +
                             endtime + " minutes. No bets are within 5 minutes of the "
                                       "timer. That means there is no winner this round!")

            print("endtime: " + endtime)
            print("endtime - 5: " + str(int(endtime) - 5))
            print("endtime + 5: " + str(int(endtime) + 5))
            print("winning time: " + str(winningtime))
        except Exception as errormsg:
            errorlog(errormsg, 'Bonertimer/stoptimer()', message)
        else:
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevBets.txt', 'a+')as f:
                f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                        str(time.strftime("%X")) + "\n")
                f.write("Endtime: %s minutes\n" % endtime)
                for key in bets:
                    f.write(key + ":" + str(bets[key]) + "\n")
            bets = {}
            with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
                f.write('')

    else:
        send_message(s, "There is currently no timer active!")


def timer(s):
    try:
        if timeractive:
            timenow = datetime.time(datetime.now())
            timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                               starttime)
            timer = str(timer).split('.')[0]
            timersplit = timer.split(':')
            endtime = ":".join(timersplit)
            send_message(s, "Fid has been alive for: " + endtime)
        else:
            send_message(s, "There is currently no timer active!")
    except Exception as errormsg:
        errorlog(errormsg, "BonerTimer/timer()", '')


def resettimer(s):
    global timeractive; global betsopen; global timers
    try:
        timeractive = False
        betsopen = True
        for t in list(timers.values()):
            t.cancel()
        time.sleep(1)
        timers = {}
        send_message(s, "Timer reset. Bets are now open again!")
    except Exception as errormsg:
        errorlog(errormsg, "BonerTimer/resettimer()", '')


def fidwins(s):
    global timeractive; global timers; global bets
    try:
        if timeractive:
            timeractive = False
            for t in list(timers.values()):
                t.cancel()
            time.sleep(1)
            timers = {}
            with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
                f.write("FideliasFK")
            timenow = datetime.time(datetime.now())
            timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                               starttime)
            endtime = str(timer).split(':')[1]
            if str(timer).split(':')[0] == '1':
                endtime += (int(endtime) + 60)
            if str(timer).split(':')[0] == '2':
                endtime += (int(endtime) + 120)
            send_message(s, "The timer is on " + endtime + " minute(s)!")
            send_message(s, "No boners have been broken this round. The winner is FideliasFK!")
        else:
            send_message(s, "There is no timer active!")
    except Exception as errormsg:
        send_message(s, "Error lettting fid win.")
        errorlog(errormsg, 'Bonertimer/fidwins', '')
    else:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevBets.txt', 'a+')as f:
            f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                    str(time.strftime("%X")) + "\n")
            f.write("Endtime: %s minutes\n" % endtime)
            for key in bets:
                f.write(key + ":" + str(bets[key]) + "\n")
        bets = {}
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
            f.write('')


def winner(s, message):
    global timeractive; global timers; global bets
    try:
        winner = message.split(" ")[1]
        if timeractive:
            timeractive = False
            for t in list(timers.values()):
                t.cancel()
            time.sleep(1)
            timers = {}
            with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
                f.write(winner)
            send_message(s, "The winner this round is %s!" % winner)
        else:
            send_message(s, "There is no timer active!")
    except IndexError:
        send_message(s, "Error setting new winner. Check your command.")
    except Exception as errormsg:
        send_message(s, "There was an error setting %s as winner." % winner)
        errorlog(errormsg, 'Bonertimer/winner()', message)
    else:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/PrevBets.txt', 'a+')as f:
            f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                    str(time.strftime("%X")) + "\n")
            f.write("No endtime available\n")
            for key in bets:
                f.write(key + ":" + str(bets[key]) + "\n")
        bets = {}
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
            f.write('')


def openbets(s):
    global betsopen
    if not betsopen:
        betsopen = True
        send_message(s, "Taking bets for the Broken Boner game! "
                     "Use !bet <number> to join in!")
    else:
        send_message(s, "Bets already opened!")


def closebets(s):
    global betsopen
    betsopen = False
    send_message(s, "Bets are now closed!")


def setboner(s, message):
    try:
        keyword = "!setboner "
        titleholder = message[message.index(keyword) + len(keyword):]
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "w") as f:
            f.write(titleholder)
        send_message(s, "Registered " + titleholder + " as the new owner of \"Broken Boner\" ")
    except ValueError:
        send_message(s, "Unable to determine new titleholder. Please check your command.")

    except Exception as errormsg:
        send_message(s, "Error changing broken boner. Error logged.")
        errorlog(errormsg, 'Bonertimer/setboner()', message)


def currentboner(s):
    try:
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Titleholder.txt", "r") as f:
            titleholder = f.read()
        send_message(s, "The current owner of the title \"Broken Boner\" is: " +
                     titleholder + "!")
    except Exception as errormsg:
        errorlog(errormsg, 'Bonertimer/currentboner()', '')
        send_message(s, "Error reading current boner")


def brokenboner(s):
    send_message(s, "The game is to bet how long it takes for Fid to break a leg or "
                 "die in ARMA. "
                 "The timer usually starts after the teleport pole or as the convoy moves out. "
                 "Anyone can join to try and win the title \"Broken Boner\"! "
                 "Use !bet <minutes> to place your bets!")


def betstats(s):
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
            send_message(s, str(length) + " people are betting this round. The lowest bet is "
                         + str(lowest) + " minutes and the highest bet is "
                         + str(highest) + " minutes. The average is " + str(avg) +
                         " minutes.")
        except Exception as errormsg:
            errorlog(errormsg, 'Bonertimer/betstats', '')
            send_message(s, "Error calculating numbers")
    else:
        send_message(s, "No bets registered!")


def bet(s, displayname, message):
    global bets; global timers
    if betsopen:
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

            keyword = "!bet "
            try:
                bet = message[message.index(keyword) + len(keyword):]
                if isinstance(int(bet), numbers.Number):
                    if int(bet) <= 0:
                        send_message(s, "Please don't try to invoke the apocalypse. Thanks.")
                    elif displayname in bets.keys():
                        bets[displayname] = bet
                        betsec = int(bet) * 60
                        t = threading.Timer(betsec, announcer, [s, displayname, bet])
                        timers[displayname] = t
                        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
                            for key in bets:
                                f.write(key + ":" + str(bets[key]) + "\n")
                        send_message(s, "@" + displayname + " Bet updated! Your new bet is: "
                                     + bet + " minutes!")
                    else:
                        bets[displayname] = bet
                        betsec = int(bet) * 60
                        t = threading.Timer(betsec, announcer, [s, displayname, bet])
                        timers[displayname] = t
                        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
                            for key in bets:
                                f.write(key + ":" + str(bets[key]) + "\n")
                        send_message(s,
                            "@" + displayname + " Bet registered: " + bet + " minutes!")
                else:
                    send_message(s, "Bet is not a number")
            except ValueError as e:
                if str(e) == 'substring not found':
                    send_message(s, "Use !bet <number> to enter the competition!")
                else:
                    send_message(s, "%s is not a valid bet. Please use whole numbers only." % bet)
            except Exception as errormsg:
                errorlog(errormsg, 'Bonertimer/bet()', message)
                send_message(s, "There was an error registering your bet. Please try again.")
        else:
            send_message(s, "This is a community game. You most be following for at least 7 days before you can join!")
    else:
        send_message(s, "Bets are not currently opened.")


def addbet(s, message):
    global bets; global timers
    try:
        addbet = message.split(' ')
        bets[addbet[1]] = addbet[2]
        t = threading.Timer((int(addbet[2]) * 60), announcer, [s, addbet[1], addbet[2]])
        timers[addbet[1]] = t
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt", 'w') as f:
            for key in bets:
                f.write(key + ":" + str(bets[key]) + "\n")
        send_message(s, "Bet for " + addbet[1] + " with " + addbet[2] +
                     " minutes added to pool!")
    except Exception as errormsg:
        send_message(s, "Error adding bet for this user.")
        errorlog(errormsg, 'Bonertimer/addbet()', message)


def removebet(s, message):
    global bets; global timers
    try:
        rembet = message.split(" ")[1]
        try:
            if all(i.isdigit() for i in rembet):
                if int(rembet) in list(bets.values()):
                    if list(bets.values()).count(int(rembet)) > 1:
                        userbets = []
                        index = 0
                        for i in list(bets.values()):
                            if int(rembet) == i:
                                userbets.append(list(bets.keys())[index])
                            index += 1
                        send_message(s, "Found more than one bet of " + rembet +
                                     " by these users: " + str(userbets))

                    else:
                        rembet = list(bets.keys())[list(bets.values()).index(int(rembet))]
                        del bets[rembet]
                        del timers[rembet]
                        send_message(s, "Bet for " + rembet + " removed from pool.")
                else:
                    raise Exception
            else:
                if rembet in list(bets.keys()):
                    del bets[rembet]
                    del timers[rembet]
                    send_message(s, "Bet for " + rembet + " removed from pool")
                else:
                    raise Exception
        except Exception:
            send_message(s, "There are no bets with this name or value.")
        else:
            with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Bets.txt', 'w') as f:
                for key in bets:
                    f.write(key + ":" + str(bets[key]) + "\n")

    except Exception as errormsg:
        send_message(s, "Error removing user from current pool.")
        errorlog(errormsg, 'Bonertimer/removebet()', message)


def clearbets(s):
    global bets; global timers
    try:
        bets = {}
        timers = {}
        send_message(s, "Bets cleared!")
    except Exception as errormsg:
        send_message(s, "Error clearing the bets. Error logged.")
        errorlog(errormsg, 'Bonertimer/clearbets()', '')


def mybet(s, displayname):
    try:
        if bets.get(displayname):
            send_message(s, displayname + " your bet is: " +
                         str(bets.get(displayname)) + " minutes!")
        else:
            send_message(s, "No bet registered!")
    except Exception as errormsg:
        send_message(s, "There was an error showing your bet!")
        errorlog(errormsg, 'Bonertimer/mybet()', '')


def addending(s, message):
    try:
        keyword = "!addending "
        newending = message[message.index(keyword) + len(keyword):]
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Endings.txt", "a") as f:
            f.write(newending + "\n")
        send_message(s, "Ending added to the list!")
    except Exception as errormsg:
        send_message(s, "There was an error registering your text. Please try again!")
        errorlog(errormsg, 'Bonertimer/addending()', message)
