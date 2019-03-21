import sys
import os
import ctypes
import socket
import ast
import configparser
import logging
import requests
import validators
from unidecode import unidecode

# Append path to modules to path variable and load custom modules
sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')
from Roulette import *
from Sendmessage import *
from Getgame import *  # TODO Keep as seperate module?
from Backseatmessage import *
from Errorlog import *
from Logger import *
from Quotes import *
from Raffles import *
from Deathcounter import *
from Rules import *
from BonerTimer import *
from RimworldAutomessage import load_rimworldautomessage
from Paddle import *
from Questions import *
from Modlog import *
from Conversions import *
from Random_stuff import *  # TODO split into seperate modules
from RimworldModLinker import *
from SongSuggestions import *
from Database import load_database
from CustomCommands import *


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
           'CC': {"name": 'CustomCommands'}}

# Enabling modules if set to true in config file
modulesConfig = config['Modules']
for module in modules.keys():
    modules[module]["enabled"] = modulesConfig.getboolean(modules[module]["name"])
    modules[module]["functions"] = {}
    if modules[module]["enabled"]:
        tree = parse_ast("../modules/" + modules[module]["name"] + ".py")
        for func in top_level_functions(tree.body):
            modules[module]["functions"][func.name] = {"next use": time.time()}


logging.debug("Loaded config.")
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


def enabled(module):
    return modules[module]["enabled"]


def oncooldown(module, func):
    if modules[module]["functions"][func]["next use"] <= time.time():
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
        errorlog(errormsg, "logline()", line)


def nopong():  # Function to restart the bot in case of connection lost
    errorlog("Connection lost, bot restarted", "nopong", '')
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
    load_send_message(FOLDER, CHANNEL, s)
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
    load_database(FOLDER)

    if modules['RU']["enabled"]:
        load_rules(FOLDER)
    if modules['BSM']["enabled"]:
        load_bsmessage(FOLDER)
    if modules['DC']["enabled"]:
        load_deaths(FOLDER)
    if modules['QU']["enabled"]:
        load_quotes(FOLDER)
    if modules['RF']["enabled"]:
        load_raffles(CLIENTID, channel_id)
    if modules['BT']["enabled"]:
        load_bonertimer(FOLDER)
    if modules['RA']["enabled"]:
        load_rimworldautomessage(FOLDER, channel_id, CLIENTID)
    if modules['QS']["enabled"]:
        load_questions(FOLDER)
    if modules['ML']["enabled"]:
        load_modlog(channel_id, headers, FOLDER)
    if modules['FG']["enabled"]:
        load_followergoals(FOLDER)
    if modules['RML']["enabled"]:
        load_mod(STEAMAPIKEY)
    if modules['BT']["enabled"]:
        load_suggestions(FOLDER)
    if modules['SS']['enabled']:
        load_suggestions(FOLDER)
    if modules['CC']['enabled']:
        customcommands = load_commands()

    logging.debug("Loaded modules")
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
                        errorlog(errormsg, "keepalivetimer", '')

                    # if modules["FG"]["Enabled"]:
                    #     try:
                    #         followergoal(channel_id, CHANNEL, CLIENTID)
                    #     except Exception as errormsg:
                    #         errorlog(errormsg, "Main/followergoal()", "")

                    if enabled("BSM"):
                        bsmcheck(channel_id, CLIENTID)

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)
                    if printparts:
                        print(parts)
                    if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "ACK" not in \
                            parts[1]:
                        issub = False
                        ismod = False

                    if "CLEARCHAT" in parts[1] and enabled("ML"):
                        modlog(parts)

                    templist = ['QUIT', 'JOIN', 'PART', 'ACK', 'USERSTATE', 'ROOMSTATE', 'CLEARCHAT', "NOTICE",
                                'HOSTTARGET']
                    try:
                        tempparts = parts[1].split(" ")
                    except:
                        tempparts = parts[0].split(" ")

                    if "NOTICE" in tempparts[1]:
                        print(">>>" + parts[2][:len(parts[2]) - 1])

                    if not any(s in tempparts[1] for s in templist):
                        # noinspection PyBroadException
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
                            subindex = subindex[0]
                            modindex = modindex[0]
                            displayindex = displayindex[0]
                            if tags[displayindex] != 'display-name=':
                                displayname = tags[displayindex]
                                displayname = displayname.split("=")[1]
                                displayname = displayname.replace("\\s", '')

                            if tags[subindex] == 'subscriber=1' or 'subscriber' in tags[0]:
                                issub = True
                            else:
                                issub = False

                            if tags[modindex] == 'mod=1' or 'mod' in tags[0] or 'broadcaster' in tags[0]:
                                ismod = True
                            else:
                                ismod = False

                            if printmessage:
                                if message != "":
                                    print(displayname + ": " + message)

                            if message != "":
                                logger(displayname, message, issub, ismod)

                            # Unshortener TODO fix this thing
                            # if enabled("US"):
                            #     tempmessage = message.split(" ")
                            #     for shorturl in tempmessage:
                            #         if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                            #             unshorten(shorturl)

                            # These are the actual commands
                            if message == "":
                                pass

                            elif message[0] == '!':
                                cooldown_time = 0
                                try:
                                    messagelow = message.lower()
                                    if messagelow == "!test":
                                        send_message("Test successful. Bot is online!")

                                    elif "!pun" in messagelow and not oncooldown("other", "pun"):
                                        func = "pun"
                                        cooldown_time = 30

                                        pun()

                                    elif "!commandlist" in messagelow and not oncooldown("other", "commandlist"):
                                        func = "commandlist"
                                        cooldown_time = 30

                                        send_message(f"Commands for this channel can be found here: "
                                                     f"http://www.bastixx.nl/twitch/{FOLDER}/commands.php")

                                    if enabled("RU"):
                                        module = "RU"
                                        if "!rule" in messagelow and ismod and not oncooldown(module, "rule"):
                                            func = "rule"
                                            cooldown_time = 5

                                            func_rules(message)

                                    if enabled("DC"):
                                        module = "DC"
                                        if "!deaths" in messagelow and not oncooldown(module, "deaths"):
                                            func = "deaths"

                                            game = str(getgame(channel_id, CLIENTID)).lower()
                                            cooldown_time = func_deaths(message, game, ismod)

                                        if messagelow == "!dead" and not oncooldown(module, "dead") and (ismod or issub):
                                            func = "dead"
                                            cooldown_time = 10

                                            game = str(getgame(channel_id, CLIENTID)).lower()
                                            dead(game)

                                    if enabled("RF"):
                                        module = "RF"
                                        if "!raffle" in messagelow and ismod:
                                            func = "raffle"
                                            cooldown_time = 5

                                            raffle(message)

                                        elif "!join" in messagelow:
                                            join_raffle(displayname, message, issub, ismod)

                                    if enabled("RO"):
                                        module = "RO"
                                        if "!roulette" in messagelow and not oncooldown(module, "roulette"):
                                            func = "roulette"
                                            cooldown_time = 20

                                            roulette(displayname)

                                    if enabled("PA"):
                                        module = "PA"
                                        if "!paddle" in message and not oncooldown(module, "paddle"):
                                            func = "paddle"
                                            cooldown_time = 20

                                            paddle(displayname, message)

                                    if enabled("QU"):
                                        module = "QU"
                                        if messagelow == "!lastquote" and (not oncooldown(module, "last_quote") or ismod):
                                            func = "last_quote"
                                            cooldown_time = 15

                                            last_quote()

                                        elif "!quote" in messagelow and (not oncooldown(module, "quote") or ismod):
                                            func = "quote"
                                            cooldown_time = 15

                                            game = getgame(channel_id, CLIENTID)
                                            quote(message, game)

                                    if enabled("BSM"):
                                        if "!backseatmessage" in messagelow or '!bsm' in messagelow and ismod:
                                            backseatmessage(message)

                                    if enabled("BT"):
                                        module = "BT"
                                        if "!starttimer" in messagelow and ismod and ismod:
                                            starttimer()

                                        elif "!stoptimer" in messagelow and ismod:
                                            stoptimer()

                                        elif "!openbets" in messagelow and ismod:
                                            openbets()

                                        elif "!closebets" in messagelow and ismod:
                                            closebets()

                                        elif messagelow == "!betstats":
                                            betstats()

                                        elif "!bet" in messagelow:

                                            bet(displayname, message, ismod)

                                        elif "!mybet" in messagelow:
                                            mybet(displayname)

                                        elif "!clearbets" in messagelow and ismod:
                                            clearbets()

                                        elif "!addbet" in messagelow and ismod:
                                            addbet(message)

                                        elif ("!rembet" or "!removebet") in messagelow and ismod:
                                            removebet(message)

                                        elif "!currentboner" in messagelow and not oncooldown(module, "currentboner"):
                                            func = "currentboner"
                                            cooldown_time = 30
                                            currentboner()

                                        elif "!brokenboner" in messagelow and not oncooldown(module, "brokenboner"):
                                            func = "brokenboner"
                                            cooldown_time = 30
                                            brokenboner()

                                        elif "!setboner" in messagelow and ismod:
                                            setboner(message)

                                        elif "!timer" in messagelow and not oncooldown(module, "timer"):
                                            func = "timer"
                                            cooldown_time = 30
                                            timer()

                                        elif "!resettimer" in messagelow and ismod:
                                            resettimer()

                                        elif "!fidwins" in messagelow and ismod:
                                            fidwins()

                                        elif "!winner" in messagelow and ismod:
                                            winner(message)

                                    if enabled("QU"):
                                        module = "QU"
                                        if message == "!question" and not oncooldown(module, "question"):
                                            func = "question"
                                            cooldown_time = 30

                                            question(message)

                                        elif "!addquestion" in message and ismod:
                                            add_question(message)

                                        elif "!removequestion" in message and ismod and not oncooldown(module, "remove_question"):
                                            func = "remove_question"
                                            cooldown_time = 2

                                            remove_question(message)

                                    if "!bot" in messagelow:
                                        send_message("This bot is made by Bastixx669. "
                                                     "Github: https://github.com/bastixx/ModularBot")

                                    if enabled("CV"):
                                        module = "CV"
                                        if "!convert" in messagelow and not oncooldown(module, "convert"):
                                            func = "convert"
                                            cooldown_time = 10
                                            convert(message)

                                    if enabled("RML"):
                                        module = "RML"
                                        if "!linkmod" in messagelow and not oncooldown(module, "linkmod"):
                                            func = "linkmod"
                                            cooldown_time = 15

                                            linkmod(message)

                                    if enabled("SS"):
                                        module = "SS"
                                        if "!suggest" in messagelow and (not oncooldown(module, "suggest")or ismod):
                                            func = "suggest"
                                            cooldown_time = 5

                                            suggest(message)

                                        elif "!clearsuggestions" in messagelow and ismod:
                                            clearsuggestions()

                                    if enabled("CC"):
                                        module = "CC"
                                        if "!command" in messagelow and ismod:
                                            func_command(message)
                                        else:
                                            if messagelow.split(" ")[0] in customcommands.keys():
                                                eval_command(message)


                                    if messagelow == '!restart' and username == 'bastixx669':
                                        nopong()

                                    elif "!module" in messagelow and username == 'bastixx669':
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
                                                                send_message("Module already enabled.")
                                                                var_break = True
                                                        templist.append(lineinfile)
                                                    f.seek(0)
                                                    for lineinfile in templist:
                                                        f.write(lineinfile)
                                                if not var_break:
                                                    send_message(f"Module {keyword} enabled.")
                                                    nopong()
                                            except Exception as errormsg:
                                                errorlog(errormsg, "module/enable", message)
                                                send_message("Error enabling this module.")
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
                                                                send_message("Module already disabled.")
                                                                var_break = True
                                                        templist.append(lineinfile)
                                                    f.seek(0)
                                                    for lineinfile in templist:
                                                        f.write(lineinfile)
                                                if not var_break:
                                                    send_message(f"Module {keyword} disabled.")
                                                    nopong()
                                            except Exception as errormsg:
                                                errorlog(errormsg, "module/disable", message)
                                                send_message("Error disabling this module.")
                                finally:
                                    if cooldown_time != 0:
                                        modules[module]["functions"][func] = {"next use": time.time() + cooldown_time}

                        for l in parts:
                            if "End of /NAMES list" in l:
                                modt = True
                                print(">>>Bot ready in channel: %s" % CHANNEL.decode())
                                logger('>>>Bot', f'Bot ready in channel {CHANNEL.decode()}', False, True)
                                modulelist = []
                                for module in modules.keys():
                                    modulelist.append(module)
                                print(">>>modules loaded: %s" % ", ".join(modulelist))

        except Exception as errormsg:
            try:
                errorlog(errormsg, 'Main()', temp)
            except Exception:
                errorlog(errormsg, 'Main()', '')
            raise errormsg


main()
# todo add cache for follows
# todo rework bonertimer module
# todo stramline functions/names
