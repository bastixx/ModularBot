import sys
import os
import ctypes
import socket
import ast
import configparser
import logging
import threading
import re

import requests
import time
import validators
from unidecode import unidecode

# Append path to modules to path variable and load custom modules
# sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')
# from Required.Sendmessage import *
# from Required.Getgame import *  # TODO Keep as seperate module?
# from Required.Tagger import *
# from Required.Errorlog import *
# from Required.Logger import *
# from Backseatmessage import *
# from Roulette import *
# from Quotes import *
# from Raffles import *
# from Deathcounter import *
# from Rules import *
# from BonerTimer import *
# from RimworldAutomessage import load_rimworldautomessage
# from Paddle import *
# from Questions import *
# from Modlog import *
# from Conversions import *
# from Random_stuff import *  # TODO split into seperate modules
# from RimworldModLinker import *
# from SongSuggestions import *
# from Required.Database import load_database
# from CustomCommands import *
# from responseParse import *
from Required.Errors import *
from Required.Getgame import get_current_game
from Modules.Required import Sendmessage, Tagger, Errorlog, Logger, Database
from Modules import Backseatmessage, Roulette, Quotes, Raffles, Deathcounter, Rules, BonerTimer, RimworldAutomessage,\
    RimworldModLinker, Paddle, Questions, Modlog, Conversions, Random_stuff, SongSuggestions, CustomCommands, \
    responseParse


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


logging.basicConfig()
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
STEAMAPIKEY = settings['SteamApiKey']

# For debugging purposes
debug = config['Debug']
printmessage = debug.getboolean('Print message')
printraw = debug.getboolean('Print raw')
lograw = debug.getboolean('Log raw')
printparts = debug.getboolean('Print tags')

modules = {'SM': {"name": 'Sendmessage'},
           'EL': {"name": 'Errorlog'},
           'LO': {"name": 'Logger'},
           'DC': {"name": 'Deathcounter'},
           'QU': {"name": 'Quotes'},
           'RF': {"name": 'Raffles'},
           'RO': {"name": 'Roulette'},
           'BSM': {"name": 'Backseatmessage'},
           'RU': {"name": 'Rules'},
           'BT': {"name": 'BonerTimer'},
           'RA': {"name": 'RimworldAutomessage'},
           'PA': {"name": 'Paddle'},
           'QS': {"name": 'Questions'},
           'ML': {"name": 'Modlog'},
           'CV': {"name": 'Conversions'},
           'FG': {"name": 'FollowerGoals'},
           'RML': {"name": 'RimworldModLinker'},
           'SS': {"name": 'SongSuggestions'},
           'CC': {"name": 'CustomCommands'},
           'RP': {"name": 'ResponseParse'}}

# Enabling modules if set to true in config file
modulesConfig = config['Modules']
for module in modules.keys():
    modules[module]["enabled"] = modulesConfig.getboolean(modules[module]["name"])
    modules[module]["functions"] = {}
    if modules[module]["enabled"]:
        tree = parse_ast("../modules/" + modules[module]["name"] + ".py")
        for func in top_level_functions(tree.body):
            modules[module]["functions"][func.name] = {"next use": time.time()}


modules['other'] = {"name": "Other"}
# logging.debug("Loaded config.")
# filter(lambda x: modules[x]["enabled"], modules.keys())

# setting the name of the window to bot name for easier distinguishing
ctypes.windll.kernel32.SetConsoleTitleW(f"{FOLDER}")

# Connecting to Twitch IRC by passing credentials and joining a certain channel
sock = socket.socket()
sock.connect((HOST, PORT))
sock.send(b"PASS " + PASS + b"\r\n")
sock.send(b"NICK " + NICK + b"\r\n")
# Sending a command to make twitch return tags with each message
sock.send(b"CAP REQ :twitch.tv/tags \r\n")
sock.send(b"CAP REQ :twitch.tv/commands \r\n")
# Join the IRC channel of the channel
sock.send(b"JOIN #" + CHANNEL + b"\r\n")


def enabled(module): # MB use this in the giant List of modules?
    return modules[module]["enabled"]


def oncooldown(module, func):
    print("Next use:")
    print(modules[module]["functions"][func]["next use"])
    print("time.time:")
    print(time.time())
    print("on cooldown:")
    print(modules[module]["functions"][func]["next use"] >= time.time())
    if modules[module]["functions"][func]["next use"] >= time.time():
        return True
    else:
        return False


def command_limiter(command):  # Allows for cooldowns to be set on commands
    global comlimits
    comlimits.remove(command)


def logline(line):  # Debug setting to save the raw data recieved to a file
    try:
        line = unidecode(line)
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{FOLDER}/files/chatlogs/raw-" + time.strftime(
                "%d-%m-%Y") + ".txt", 'a+') as f:
            f.write("[%s] %s\n" % (str(time.strftime("%H:%M:%S")), line))
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, "logline()", line)


def nopong():  # Function to restart the bot in case of connection lost
    Errorlog.errorlog("Connection lost, bot restarted", "nopong", '')
    os.execv(sys.executable, [sys.executable, f"{os.path.dirname(__file__)}/{FOLDER}/{FOLDER}.py"] + sys.argv)


def main(s=sock):
    global comlimits
    readbuffer = ""
    modt = False
    comlimits = []

    # Starting the timer in case of a disconnect
    keepalivetimer = threading.Timer(310, nopong)
    keepalivetimer.start()

    # Loading the basic modules
    Tagger.load_tagger(CLIENTID)
    Sendmessage.load_send_message(FOLDER, CHANNEL, s)
    Errorlog.load_errorlog(FOLDER)

    # Resolve user id to channel id via the Twitch API
    try:
        url = "https://api.twitch.tv/helix/users?login=" + CHANNEL.decode()
        headers = {'Client-ID': CLIENTID, 'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': "OAuth " + OAUTH}
        r = requests.get(url, headers=headers).json()
        channel_id = r['data'][0]['id']
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, 'Twitch API/get Client_id', '')
        exit(0)

    # Load all the modules that were enabled in the config file
    Database.load_database(FOLDER)
    # load_tagger()

    if enabled("RU"):
        Rules.load_rules()
    if enabled("BSM"):
        Backseatmessage.load_bsmessage()
    if enabled("DC"):
        Deathcounter.load_deaths()
    if enabled("QU"):
        Quotes.load_quotes(FOLDER)
    if enabled("RF"):
        Raffles.load_raffles(CLIENTID, channel_id)
    if enabled("BT"):
        BonerTimer.load_bonertimer(FOLDER)
    if enabled("RA"):
        RimworldAutomessage.load_rimworldautomessage(channel_id, CLIENTID)
    if enabled("QS"):
        Questions.load_questions()
    if enabled("ML"):
        Modlog.load_modlog(channel_id, headers)
    if enabled("FG"):
        Random_stuff.load_followergoals(FOLDER)
    if enabled("RML"):
        RimworldModLinker.load_mod(STEAMAPIKEY)
    if enabled("SS"):
        SongSuggestions.load_suggestions()
    if enabled("CC"):
        customcommands = CustomCommands.load_commands()
    if enabled("RP"):
        responseParse.load_responses()

    # Infinite loop waiting for commands
    while True:
        try:
            # Read messages from buffer to temp, which we then line by line disect.
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
                        Errorlog.errorlog(errormsg, "keepalivetimer", '')

                    # if modules["FG"]["Enabled"]:
                    #     try:
                    #         followergoal(channel_id, CHANNEL, CLIENTID)
                    #     except Exception as errormsg:
                    #         Errorlog.errorlog(errormsg, "Main/followergoal()", "")

                    if enabled("BSM"):
                        Backseatmessage.bsmcheck(channel_id, CLIENTID)

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)

                    # Only works after twitch is done announcing stuff (modt = Message of the day)
                    if modt:
                        if line.find("PRIVMSG") != -1:
                            displayname, username, userid, message, issub, ismod = Tagger.tagprivmsg(line)
                            msgtype = "PRIVMSG"
                        elif line.find("CLEARCHAT") != -1:
                            Tagger.tagclearchat(line)
                            msgtype = "CLEARCHAT"
                        elif line.find("CLEARMSG") != -1:
                            Tagger.tagclearmsg(line)
                            msgtype = "CLEARMSG"
                        elif line.find("USERNOTICE") != -1:
                            Tagger.tagusernotice(line)
                            msgtype = "USERNOTICE"
                        elif line.find("USERSTATE") != -1:
                            msgtype = "USERSTATE"
                        elif line.find("NOTICE") != -1:
                            Tagger.tagnotice(line)
                            msgtype = "NOTICE"

                        if msgtype == "PRIVMSG":
                            Logger.logger(userid, displayname, message, issub, ismod)

                        # Unshortener TODO fix this thing
                        # if enabled("US"):
                        #     tempmessage = message.split(" ")
                        #     for shorturl in tempmessage:
                        #         if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                        #             unshorten(shorturl)

                        # These are the actual commands
                        if msgtype != "PRIVMSG":
                            pass

                        elif message[0] == '!':
                            cooldown_time = 0
                            try:
                                messagelow = message.lower()
                                if messagelow == "!test":
                                    Sendmessage.send_message("Test successful. Bot is online!")

                                elif "!pun" in messagelow[0:4] and not oncooldown("other", "pun"):
                                    functionname = "pun"
                                    cooldown_time = 30

                                    Random_stuff.pun()

                                elif "!commandlist" in messagelow[0:12] and not oncooldown("other", "commandlist"):
                                    functionname = "commandlist"
                                    cooldown_time = 30

                                    Sendmessage.send_message(f"Commands for this channel can be found here: "
                                                             f"http://www.bastixx.nl/twitch/{FOLDER}/commands.php")

                                if enabled("RU"):
                                    if "!rule" in messagelow[0:5] and ismod and not oncooldown("RU", "rule"):
                                        custommodule = "RU"
                                        functionname = "rule"
                                        cooldown_time = 5

                                        Rules.func_rules(message)

                                if enabled("DC"):
                                    if "!deaths" in messagelow[0:7] and not oncooldown("DC", "func_deaths"):
                                        custommodule = "DC"
                                        functionname = "func_deaths"

                                        game = str(get_current_game(channel_id, CLIENTID)).lower()
                                        cooldown_time = Deathcounter.func_deaths(message, game, ismod)

                                    if "!dead" in messagelow[0:5] and not oncooldown("DC", "dead") and (ismod or issub):
                                        custommodule = "DC"
                                        functionname = "dead"
                                        cooldown_time = 10

                                        game = str(get_current_game(channel_id, CLIENTID)).lower()
                                        Deathcounter.dead(game)

                                if enabled("RF"):
                                    if ("!raffle" in messagelow[0:7] or "!giveaway" in messagelow[0:9]) and ismod:
                                        custommodule = "RF"
                                        functionname = "raffle"
                                        cooldown_time = 5

                                        Raffles.raffle(message)

                                    elif "!join" in messagelow[0:5]:
                                        custommodule = "RF"
                                        Raffles.join_raffle(displayname, message, issub, ismod)

                                if enabled("RO"):
                                    if "!roulette" in messagelow[0:9] and not oncooldown("RO", "roulette"):
                                        custommodule = "RO"
                                        functionname = "roulette"
                                        cooldown_time = 20

                                        Roulette.roulette(displayname)

                                if enabled("PA"):
                                    if "!paddle" in messagelow[0:7] and not oncooldown("PA", "paddle"):
                                        custommodule = "PA"
                                        try:
                                            cooldown_time = 20
                                            functionname = "paddle"
                                            Paddle.paddle(displayname, message)

                                        except InsufficientParameterException:
                                            cooldown_time = 0
                                            Sendmessage.send_message("Usage: !paddle <username>")

                                        except KeyError:
                                            pass

                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "!paddle", message)

                                if enabled("QU"):
                                    if "!lastquote" in messagelow[0:10] and (not oncooldown("QU", "last_quote") or ismod):
                                        custommodule = "QU"
                                        functionname = "last_quote"
                                        cooldown_time = 15

                                        Quotes.last_quote()

                                    elif "!quote" in messagelow[0:6] and (not oncooldown("QU", "quote") or ismod):
                                        custommodule = "QU"
                                        functionname = "quote"
                                        cooldown_time = 15

                                        game = get_current_game(channel_id, CLIENTID)
                                        Quotes.quote(message, game)

                                if enabled("BSM"):
                                    if ("!backseatmessage" in messagelow[0:16] or '!bsm' in messagelow[0:4]) and ismod:
                                        Backseatmessage.backseatmessage(message)

                                if enabled("BT"):
                                    if "!starttimer" in messagelow[0:11] and ismod and ismod:
                                        custommodule = "BT"
                                        BonerTimer.timer(message)

                                    elif "!stoptimer" in messagelow[0:10] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.timer(message)

                                    elif "!openbets" in messagelow[0:9] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.bets(message)

                                    elif "!closebets" in messagelow[0:10] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.bets(message)

                                    elif "!betstats" in messagelow[0:9]:
                                        custommodule = "BT"
                                        BonerTimer.betstats()

                                    elif "!bet" in messagelow[0:4]:
                                        custommodule = "BT"
                                        BonerTimer.bet(displayname, message, ismod)

                                    elif "!mybet" in messagelow[0:6]:
                                        custommodule = "BT"
                                        BonerTimer.mybet(displayname)

                                    elif "!clearbets" in messagelow[0:10] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.clearbets()

                                    elif "!addbet" in messagelow[0:7] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.addbet(message)

                                    elif ("!rembet" in messagelow[0:7] or "!removebet" in messagelow[0:10])and ismod:
                                        custommodule = "BT"
                                        BonerTimer.removebet(message)

                                    elif "!currentboner" in messagelow[0:13] and not oncooldown("BT", "currentboner"):
                                        custommodule = "BT"
                                        functionname = "currentboner"
                                        cooldown_time = 30
                                        BonerTimer.currentboner()

                                    elif "!brokenboner" in messagelow[0:12] and not oncooldown("BT", "brokenboner"):
                                        custommodule = "BT"
                                        functionname = "brokenboner"
                                        cooldown_time = 30
                                        BonerTimer.brokenboner()

                                    elif "!setboner" in messagelow[0:9] and ismod:
                                        BonerTimer.setboner(message)

                                    elif "!timer" in messagelow[0:6] and not oncooldown("BT", "timer"):
                                        custommodule = "BT"
                                        functionname = "timer"
                                        cooldown_time = 30
                                        BonerTimer.timer(message)

                                    elif "!resettimer" in messagelow[0:11] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.timer(message)

                                    elif "!fidwins" in messagelow[0:8] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.fidwins()

                                    elif "!winner" in messagelow[0:7] and ismod:
                                        custommodule = "BT"
                                        BonerTimer.winner(message)

                                if enabled("QU"):
                                    if "!question" in messagelow[0:9] and not oncooldown("QU", "question"):
                                        custommodule = "QU"
                                        functionname = "question"
                                        cooldown_time = Questions.question(message, ismod)

                                if "!bot" in messagelow[0:4]:
                                    Sendmessage.send_message("This bot is made by Bastixx669. "
                                                             "Github: https://github.com/bastixx/ModularBot")

                                if enabled("CV"):
                                    if "!convert" in messagelow[0:8] and not oncooldown("CV", "convert"):
                                        custommodule = "CV"
                                        functionname = "convert"
                                        cooldown_time = 10
                                        Conversions.convert(message)

                                if enabled("RML"):
                                    if "!linkmod" in messagelow[0:8] and not oncooldown("RML", "linkmod"):
                                        custommodule = "RML"
                                        functionname = "linkmod"
                                        cooldown_time = 15

                                        RimworldModLinker.linkmod(message)

                                if enabled("RA"):
                                    if "!rimworldmessage" in messagelow[0:15]:
                                        custommodule = "RA"
                                        functionname = "setmessage"
                                        RimworldAutomessage.setmessage(message)

                                if enabled("SS"):
                                    if "!suggest" in messagelow[0:8] and (not oncooldown("SS", "suggest")or ismod):
                                        custommodule = "SS"
                                        functionname = "suggest"
                                        cooldown_time = 5

                                        SongSuggestions.suggest(message)

                                    elif "!clearsuggestions" in messagelow[0:17] and ismod:
                                        custommodule = "SS"
                                        SongSuggestions.clearsuggestions()

                                if enabled("CC"):
                                    if "!command" in messagelow[0:8] and ismod:
                                        custommodule = "CC"
                                        CustomCommands.func_command(message)
                                    else:
                                        if messagelow.split(" ")[0] in customcommands.keys():
                                            CustomCommands.eval_command(message)

                                if '!restart' in messagelow[0:8] and username == 'bastixx669':
                                    nopong()

                                elif "!module" in messagelow[0:7] and username == 'bastixx669':
                                    messageparts = message.split(" ")
                                    var_break = False
                                    if messageparts[1] == "enable":
                                        try:
                                            templist = []
                                            keyword = " ".join(messageparts[2:])
                                            with open('config.ini', 'r+') as f:
                                                for lineinfile in f:
                                                    if keyword in lineinfile:
                                                        if "False" in lineinfile:
                                                            lineinfile = lineinfile.replace('False', 'True')
                                                        else:
                                                            Sendmessage.send_message("Module already enabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                Sendmessage.send_message(f"Module {keyword} enabled.")
                                                nopong()
                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "custommodule/enable", message)
                                            Sendmessage.send_message("Error enabling this custommodule.")
                                    elif messageparts[1] == "disable":
                                        try:
                                            templist = []
                                            keyword = " ".join(messageparts[2:])
                                            with open('config.ini', 'r+') as f:
                                                for lineinfile in f:
                                                    if keyword in lineinfile:
                                                        if "True" in lineinfile:
                                                            lineinfile = lineinfile.replace('True', 'False')
                                                        else:
                                                            Sendmessage.send_message("Module already disabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                Sendmessage.send_message(f"Module {keyword} disabled.")
                                                nopong()
                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "custommodule/disable", message)
                                            Sendmessage.send_message("Error disabling this custommodule.")
                            except Exception as errormsg:
                                Errorlog.errorlog(errormsg, "main/functions", message)
                                Sendmessage.send_message("There was an error with the command. "
                                                         "Please check your command and try again.")

                                print(f"Message: {message}")
                                print(f"Line: {line}")

                            finally:
                                if cooldown_time != 0:
                                    # tempdict = {custommodule: {"functions": {functionname: {"next use": time.time() + cooldown_time}}}}
                                    modules[custommodule]["functions"][functionname] = {"next use": time.time() + cooldown_time}
                                    # modules.update(tempdict)

                                    print(f"Module: {custommodule}")
                        else:
                            if enabled('RP'):
                                responseParse.parse_response(message)

                    for l in parts:
                        if "End of /NAMES list" in l:
                            modt = True
                            Logger.logger(0000000, '>>Bot', f'Bot ready in channel {CHANNEL.decode()}', False, True, True)
                            modulelist = []
                            for custommodule in modules.keys():
                                x = modules[custommodule]["name"]
                                modulelist.append(x)
                            Logger.logger(0000000, ">>Bot", "Modules loaded: %s" % ", ".join(modulelist), False, True, True)

        except Exception as errormsg:
            try:
                Errorlog.errorlog(errormsg, 'Main()', temp)
            except Exception:
                Errorlog.errorlog(errormsg, 'Main()', '')
            raise errormsg


main()
# todo add cache for follows
# todo rework bonertimer module
# todo streamline functions/names
