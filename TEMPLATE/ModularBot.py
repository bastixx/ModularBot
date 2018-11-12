import sys
import os
import ctypes
import socket
import configparser
import threading
import time
import requests
import validators
from unidecode import unidecode

# Append path do modules to path variable and load custom modules
sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')
from Roulette import roulette
from Send_message import send_message, load_send_message
from Getgame import getgame
from Backseatmessage import backseatmessage, load_bsmessage
from Errorlog import load_errorlog, errorlog
from Logger import logger, load_logger
from Quotes import load_quotes, get_quote, add_quote, remove_quote, last_quote
from Raffles import load_raffles, raffle, join_raffle
from Deathcounter import load_deaths, func_deaths, dead
from Rules import load_rules, func_rules
from BonerTimer import *
from RimworldAutomessage import load_rimworldautomessage, rimworldautomessage
from Paddle import paddle
from Questions import load_questions, question, add_question, remove_question
from Modlog import load_modlog, modlog
from Conversions import convert
from Random_stuff import unshorten, followergoal, load_followergoals


# Load all the variables necessary to connect to Twitch IRC from a config file
config = configparser.ConfigParser()
config.read('Config.ini')
settings = config['Settings']

HOST = settings['host']
NICK = b"%s" % settings['Nickname'].encode()
PORT = int(settings['port'])
PASS = b"%s" % settings['Password'].encode()
CHANNEL = b"%s" % settings['Channel'].encode()
CLIENTID = settings['Client ID']
OAUTH = PASS.decode().split(":")[1]
FOLDER = settings['Folder']

# For debugging purposes
debug = config['Debug']
printmessage = debug.getboolean('Print message')
printraw = debug.getboolean('Print raw')
lograw = debug.getboolean('Log raw')
printparts = debug.getboolean('Print tags')

# Enabling modules if set to true in config file
modules = config['Modules']
module_deathcounter = modules.getboolean('Deathcounter')
module_quotes = modules.getboolean('Quotes')
module_raffles = modules.getboolean('Raffles')
module_roulette = modules.getboolean('Roulette')
module_backseatmessage = modules.getboolean('Backseatmessage')
module_rules = modules.getboolean('Rules')
module_bonertimer = modules.getboolean('BonerTimer')
module_rimworldautomessage = modules.getboolean('Rimworld automessage')
module_paddle = modules.getboolean('Paddle')
module_questions = modules.getboolean('Questions')
module_modlog = modules.getboolean('Modlog')
module_conversion = modules.getboolean('Conversions')
module_unshorten = modules.getboolean('Unshorten')
module_followergoal = modules.getboolean('Follower goals')

# setting the name of the window to bot name for easier distinguishing
ctypes.windll.kernel32.SetConsoleTitleW(f"{FOLDER}")

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send(b"PASS " + PASS + b"\r\n")
s.send(b"NICK " + NICK + b"\r\n")
# Sending a command to make twitch return tags with each message
s.send(b"CAP REQ :twitch.tv/tags \r\n")
s.send(b"CAP REQ :twitch.tv/commands \r\n")
s.send(b"JOIN #" + CHANNEL + b"\r\n")


def command_limiter(command):  # Allows for cooldowns to be set on commands
    global comlimits
    comlimits.remove(command)


def logline(line):  # Debug setting to save the raw data recieved to a file
    try:
        line = unidecode(line)
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{FOLDER}/files/chatlogs/raw-" + time.strftime("%d-%m-%Y") + ".txt", 'a+') as f:
            f.write("[%s] %s\n" % (str(time.strftime("%H:%M:%S")), line))
    except Exception as errormsg:
        errorlog(errormsg, "logline()", line)


def nopong():  # Function to restart the bot in case of connection lost
    print(">>>Connection lost, restarting bot!")
    errorlog("Connection lost, bot restarted", "nopong", '')
    os.execv(sys.executable, [sys.executable, f"{os.path.dirname(__file__)}/{FOLDER}/{FOLDER}.py"] + sys.argv)


def main():
    global comlimits
    readbuffer = ""
    modt = False
    comlimits = []
    modules = []

    # Starting the timer in case of a disconnect
    keepalivetimer = threading.Timer(310, nopong)
    keepalivetimer.start()

    # Loading the basic modules
    load_send_message(FOLDER, CHANNEL)
    load_logger(FOLDER)
    load_errorlog(FOLDER)

    # Resolve user id to channel id via the Twitch API
    try:
        url = "https://api.twitch.tv/helix/users?login=" + CHANNEL.decode()
        headers = {'Client-ID': CLIENTID, 'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': "OAuth " + OAUTH}
        r = requests.get(url, headers=headers).json()
        channel_id = r['data'][0]['id']
    except Exception as errormsg:
        errorlog(errormsg, 'Twitch API/get Client_id', '')
        exit(0)

    # Load all the modules that were enabled in the config file
    if module_rules:
        load_rules(s, FOLDER)
        modules.append("Rules")
    if module_backseatmessage:
        backseating = load_bsmessage(FOLDER)
        modules.append("Backseatmessage")
    if module_deathcounter:
        load_deaths(FOLDER)
        modules.append("Deathcounter")
    if module_quotes:
        load_quotes(FOLDER)
        modules.append("Quotes")
    if module_raffles:
        load_raffles(FOLDER, CLIENTID, channel_id)
        modules.append("Raffles")
    if module_bonertimer:
        load_bonertimer(FOLDER)
        modules.append("Bonertimer")
    if module_rimworldautomessage:
        load_rimworldautomessage(s, FOLDER, channel_id, CLIENTID)
        modules.append("RimWorldMessage")
    if module_questions:
        load_questions(FOLDER)
        modules.append("Questions")
    if module_modlog:
        load_modlog(channel_id, headers, FOLDER)
        modules.append("Modlog")
    if module_conversion:
        modules.append("Conversions")
    if module_followergoal:
        load_followergoals()

    # Infinite loop waiting for commands
    while True:
        try:
            # Recieving messages
            readbuffer = readbuffer + s.recv(1024).decode()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:
                if printraw:
                    print(line)
                if lograw:
                    logline(line)
                # Checks if  message is PING. If so reply pong and extend the timer for a restart
                if "PING" in line:
                    s.send(b"PONG\r\n")
                    try:
                        keepalivetimer.cancel()
                        keepalivetimer = threading.Timer(310, nopong)
                        keepalivetimer.start()

                    except Exception as errormsg:
                        errorlog(errormsg, "keepalivetimer", '')

                    if module_unshorten:
                        try:
                            followergoal(s, channel_id, CHANNEL, CLIENTID)
                        except Exception as errormsg:
                            errorlog(errormsg, "")

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)
                    if printparts:
                        print(parts)
                    if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "ACK" not in parts[1]:
                        issub = False
                        ismod = False

                    if "CLEARCHAT" in parts[1] and module_modlog:
                        modlog(s, parts)

                    templist = ['QUIT', 'JOIN', 'PART', 'ACK', 'USERSTATE', 'ROOMSTATE', 'CLEARCHAT']
                    tempparts = parts[1].split(" ")

                    if not any(s in tempparts[1] for s in templist):

                        try:
                            # Sets the message variable to the actual message sent
                            message = parts[2][:len(parts[2]) - 1]
                        except:
                            message = ""
                        # Sets the username variable to the actual username
                        usernamesplit = str.split(parts[1], "!")
                        username = usernamesplit[0]
                        displayname = username
                        tags = str.split(parts[0], ';')

                        # Get index of mod and sub status dynamically because tag indexes are not fixed
                        subindex = [i for i, z in enumerate(tags) if 'subscriber' in z]
                        modindex = [i for i, z in enumerate(tags) if 'mod' in z]
                        displayindex = [i for i, z in enumerate(tags) if 'display-name' in z]

                        # Only works after twitch is done announcing stuff (modt = Message of the day)
                        if modt:
                            try:
                                subindex = subindex[0]
                                modindex = modindex[0]
                                displayindex = displayindex[0]
                                if tags[displayindex] != 'display-name=':
                                    displayname = tags[displayindex]
                                    displayname = displayname.split("=")[1]
                            except:
                                pass

                            try:
                                if tags[subindex] == 'subscriber=1' or 'subscriber' in tags[0]:
                                    issub = True
                                else:
                                    issub = False

                                if tags[modindex] == 'mod=1' or 'mod' in tags[0] or 'broadcaster' in tags[0]:
                                    ismod = True
                                else:
                                    ismod = False
                            except Exception:
                                pass
                            if printmessage:
                                if message != "":
                                    print(displayname + ": " + message)

                            if message != "":
                                logger(displayname, message, issub, ismod)

                            if module_unshorten:
                                tempmessage = message.split(" ")
                                for shorturl in tempmessage:
                                    if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                                        unshorten(s, shorturl)

                            # These are the actual commands
                            if message == "":
                                pass
                            elif message[0] == '!':
                                if message.lower() == "!test":
                                    send_message(s, "Test successful. Bot is online!")

                                if module_rules:
                                    if "!rule" in message.lower() and ismod and '!rule' not in comlimits:
                                        threading.Timer(5, command_limiter, ['!rule']).start()
                                        comlimits.append('!rule')
                                        rules, warnings = func_rules(s, rules, warnings, message)

                                if module_deathcounter:
                                    if "!deaths" in message.lower() and "!deaths" not in comlimits:
                                        game = str(getgame(channel_id, CLIENTID)).lower()

                                        cooldown_time = func_deaths(s, message, game, ismod)
                                        threading.Timer(cooldown_time, command_limiter, ['!deaths']).start()
                                        comlimits.append('!deaths')

                                    elif message.lower() == "!dead" and "!dead" not in comlimits and (ismod or issub):
                                        threading.Timer(30, command_limiter, ['!dead']).start()
                                        comlimits.append('!dead')
                                        game = str(getgame(channel_id, CLIENTID)).lower()
                                        dead(s, game)

                                if module_raffles:
                                    if "!raffle" in message.lower() and ismod:
                                        raffle(s, message)

                                    elif "!join" in message.lower():
                                        join_raffle(s, displayname, message, issub, ismod)

                                if module_roulette:
                                    if "!roulette" in message.lower() and "!roulette" not in comlimits and module_roulette:
                                        threading.Timer(20, command_limiter, ['!roulette']).start()
                                        comlimits.append('!roulette')
                                        roulette(displayname, s)

                                if module_paddle:
                                    if "!paddle" in message and "!paddle" not in comlimits:
                                        threading.Timer(20, command_limiter, ['!paddle']).start()
                                        comlimits.append('!paddle')
                                        paddle(s, displayname, message)

                                if module_quotes:
                                    if message.lower() == "!lastquote" and "!quote" not in comlimits:
                                        threading.Timer(15, command_limiter, ['!quote']).start()
                                        comlimits.append('!quote')
                                        last_quote(s)

                                    elif "!addquote" in message.lower() and ismod:
                                        game = getgame(channel_id, CLIENTID)
                                        add_quote(s, message, game)

                                    elif "!removequote" in message.lower() and ismod:
                                        remove_quote(s, message)

                                    elif"!quote" in message.lower() and "!quote" not in comlimits:
                                        if not ismod:
                                            threading.Timer(15, command_limiter, ['!quote']).start()
                                            comlimits.append('!quote')
                                        get_quote(s, message)

                                if module_backseatmessage:
                                    if "!backseatmessage" in message.lower() and ismod:
                                        backseating = backseatmessage(s, FOLDER, backseating, message)

                                if module_bonertimer:
                                    if "!starttimer" in message.lower() and ismod and ismod:
                                        starttimer(s)

                                    elif "!stoptimer" in message.lower() and ismod:
                                        stoptimer(s)

                                    elif "!openbets" in message.lower() and ismod:
                                        openbets(s)

                                    elif "!closebets" in message.lower() and ismod:
                                        closebets(s)

                                    elif message.lower() == "!betstats":
                                        betstats(s)

                                    elif "!bet" in message.lower():
                                        bet(s, displayname, message)

                                    elif "!mybet" in message.lower():
                                        mybet(s, displayname)

                                    elif "!clearbets" in message.lower() and ismod:
                                        clearbets(s)

                                    elif "!addbet" in message.lower() and ismod:
                                        addbet(s, message)

                                    elif ("!rembet" or "!removebet") in message.lower() and ismod:
                                        removebet(s, message)

                                    elif "!currentboner" in message.lower():
                                        currentboner(s)

                                    elif "!brokenboner" in message.lower():
                                        brokenboner(s)

                                    elif "!setboner" in message.lower():
                                        setboner(s, message)

                                    elif "!addending" in message.lower():
                                        addending(s, message)

                                    elif "!timer" in message.lower():
                                        timer(s)

                                    elif "!resettimer" in message.lower() and ismod:
                                        resettimer(s)

                                    elif "!fidwins" in message.lower() and ismod:
                                        fidwins(s)

                                    elif "!winner" in message.lower() and ismod:
                                        winner(s, message)

                                if module_questions:
                                    if message == "!question" and "!question" not in comlimits:
                                        if not ismod:
                                            threading.Timer(15, command_limiter, ['!question']).start()
                                            comlimits.append('!question')
                                        question(s, message)

                                    elif "!addquestion" in message and ismod and module_questions:
                                        add_question(s, message)

                                    elif "!removequestion" in message and ismod and module_questions:
                                        threading.Timer(5, command_limiter, ['!removequestion']).start()
                                        comlimits.append('!removequestion')
                                        remove_question(s, message)

                                if "!bot" in message.lower():
                                    send_message(s, "This bot is made by Bastixx669. Feel free to message him with "
                                                    "questions, idea's or cookies!")

                                if module_conversion:
                                    if "!convert" in message.lower():
                                        convert(s, message)

                                elif message.lower() == '!restart' and username == 'bastixx669':
                                    nopong()

                        for l in parts:
                            if "End of /NAMES list" in l:
                                modt = True
                                print(">>>Bot ready in channel: %s" % CHANNEL.decode())
                                logger('>>>Bot', f'Bot ready in channel {CHANNEL.decode()}', False, True)
                                print("modules loaded: %s" % ", ".join(modules))

        except Exception as errormsg:
            try:
                errorlog(errormsg, 'Main()', temp)
            except Exception:
                errorlog(errormsg, 'Main()', '')


main()
