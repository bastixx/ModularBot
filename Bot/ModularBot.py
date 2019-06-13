import socket
import datetime
import time
import logging

# Append path to modules to path variable and load custom modules
# sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')

# from Required.Getgame import *  # TODO Keep as seperate module?
# from Random_stuff import *  # TODO split into seperate modules

from Modules.Required.Errors import *
# from Modules.Required.Getgame import get_current_game
from Modules.Required import Sendmessage, Tagger, Errorlog, Logger, Database, APICalls
from Modules import Backseatmessage, Roulette, Quotes, Raffles, Deathcounter, Rules, BrokenBoner, RimworldAutomessage,\
    RimworldModLinker, Paddle, Questions, Modlog, Conversions, Unshorten, SongSuggestions, CustomCommands, \
    responseParse, Pun, FollowerGoals

def enabled(module):  # MB use this in the giant List of modules?
    return modules[module]["enabled"]


def oncooldown(module, func):
    if modules[module]["functions"][func]["next use"] >= time.time():
        return True
    else:
        return False


def command_limiter(command):  # Allows for cooldowns to be set on commands
    global comlimits
    comlimits.remove(command)


def botinstance(channelid: str, channelname: str, pipe):
    global modules
    logger = logging.getLogger(channelname)

    try:
        Logger.load_logger(channelname)
        Database.load_database(channelname)
    except Exception:
        logging.exception("Main - Error starting required modules.")
        exit(0)

    try:
        config = Database.getone("Config")
        HOST = "irc.twitch.tv"
        NICK = config["Nickname"].encode()
        PORT = 6667
        PASS = config["Password"].encode()
        CHANNEL = channelname.encode()
        CLIENTID = config["ClientID"]
        # OAUTH = PASS.decode().split(":")[1]
        STEAMAPIKEY = config['SteamAPIkey']
        # Headers for the Twitch API calls being made.

        modules = {'Sendmessage': {},
                   'Errorlog': {},
                   'Logger': {},
                   'Deathcounter': {},
                   'Quotes': {},
                   'Raffles': {},
                   'Roulette': {},
                   'Backseatmessage': {},
                   'Rules': {},
                   'BrokenBoner': {},
                   'RimworldAutomessage': {},
                   'Paddle': {},
                   'Questions': {},
                   'Modlog': {},
                   'Conversions': {},
                   'FollowerGoals': {},
                   'RimworldModLinker': {},
                   'SongSuggestions': {},
                   'CustomCommands': {},
                   'ResponseParse': {}}
                   # 'Unshorten': {},
                   # 'Pun': {}}

        # Enabling modules if set to true in config file
        for document in Database.getall('Modules'):
            modules[document["module"]] = {"enabled": document["enabled"], "mandatory": document["mandatory"]}

        Database.load_database("Modules")
        for document in Database.getall('Config'):
            modules[document["Name"]]["functionlist"] = document["functions"]

        Database.load_database(channelname)

        var_time = time.time()
        for module in modules.keys():
            modules[module]["functions"] = dict()
            if modules[module].get("functionlist", None) is None:
                continue
            for function in modules[module]["functionlist"]:
                modules[module]["functions"][function] = {"next use": var_time}

        # modules['other'] = {"name": "Other"}
    except Exception:
        logging.exception("Main - Error configuring modules dict.")
        exit(0)

    try:
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

        # Loading the basic modules
        Sendmessage.load_send_message(channelname, CHANNEL, sock)
        Database.load_database(channelname)
        APICalls.load_apicalls(CLIENTID, channelid)
    except:
        logging.exception("Main - Error connecting to twitch irc.")
        exit(0)

    try:
        if enabled("Rules"):
            if not Rules.load_rules():
                modules['Rules']["enabled"] = False
        if enabled("Backseatmessage"):
            Backseatmessage.load_bsmessage()
        if enabled("Deathcounter"):
            if not Deathcounter.load_deaths():
                modules['Deathcounter']['enabled'] = False
        if enabled("Quotes"):
            if not Quotes.load_quotes():
                modules['Quotes']['enabled'] = False
        if enabled("Raffles"):
            if not Raffles.load_raffles():
                modules['Raffles']['enabled'] = False
        if enabled("BrokenBoner"):
            BrokenBoner.load_bonertimer()
        if enabled("RimworldAutomessage"):
            RimworldAutomessage.load_rimworldautomessage()
        if enabled("Questions"):
            if not Questions.load_questions():
                modules['Questions']['enabled'] = False
        if enabled("Modlog"):
            if not Modlog.load_modlog():
                modules['Modlog']['enabled'] = False
        if enabled("FollowerGoals"):
            FollowerGoals.load_followergoals(channelname)
        if enabled("SongSuggestions"):
            SongSuggestions.load_suggestions()
        if enabled("CustomCommands"):
            if not CustomCommands.load_commands():
                modules['CustomCommands']['enabled'] = False
        if enabled("ResponseParse"):
            if not responseParse.load_responses():
                modules['ResponseParse']['enabled'] = False
    except:
        logging.exception("Main - Error loading modules.")

    global comlimits
    readbuffer = ""
    modt = False
    comlimits = []

    logging.info("Config done, entering command loop...")
    # Infinite loop waiting for commands
    while True:
        try:
            # Read messages from buffer to temp, which we then line by line disect.
            readbuffer = readbuffer + sock.recv(1024).decode()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:

                # print(line)  # testing purposes

                # Checks if  message is PING. If so reply pong and extend the timer for a restart
                if "PING" in line:
                    sock.send(b"PONG\r\n")
                    # if modules["FG"]["Enabled"]:
                    #     try:
                    #         followergoal(channel_id, CHANNEL, CLIENTID)
                    #     except Exception as errormsg:
                    #         Errorlog.errorlog(errormsg, "Main/followergoal()", "")

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)

                    # Only works after twitch is done announcing stuff (modt = Message of the day)
                    if modt:
                        msgtype = ""
                        if line.find("PRIVMSG") != -1:
                            username, userid, message, issub, ismod = Tagger.tagprivmsg(line)
                            msgtype = "PRIVMSG"
                            Logger.logger(userid, username, message)
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

                        # Unshortener TODO fix this thing
                        # if enabled("US"):
                        #     # disable("US")
                        #     tempmessage = message.split(" ")
                        #     for shorturl in tempmessage:
                        #         if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                        #             unshorten(shorturl)

                        # These are the actual commands
                        if msgtype == "PRIVMSG" and message[0] == '!':
                            cooldown_time = 0
                            try:
                                messagelow = message.lower()
                                if messagelow == "!test":
                                    Sendmessage.send_message("Test successful. Bot is online!")

                                elif "!pun" in messagelow[0:4] and not oncooldown("other", "pun"):
                                    functionname = "pun"
                                    cooldown_time = 30

                                    Pun.pun()

                                elif "!commandlist" in messagelow[0:12] and not oncooldown("other", "commandlist"):
                                    functionname = "commandlist"
                                    cooldown_time = 30

                                    Sendmessage.send_message(f"Commands for this channel can be found here: "
                                                             f"http://www.bastixx.nl/twitch/{channelname}/commands.php")

                                if enabled("Rules"):
                                    if "!rule" in messagelow[0:5] and ismod and not oncooldown("Rules", "rule"):
                                        custommodule = "Rules"
                                        functionname = "rule"
                                        cooldown_time = 5

                                        Rules.func_rules(message)

                                if enabled("Deathcounter"):
                                    if "!deaths" in messagelow[0:7] and not oncooldown("Deathcounter", "func_deaths"):
                                        custommodule = "Deathcounter"
                                        functionname = "func_deaths"

                                        cooldown_time = Deathcounter.func_deaths(message, APICalls.channel_game(), ismod)

                                    if "!dead" in messagelow[0:5] and not oncooldown("Deathcounter", "dead") and (ismod or issub):
                                        custommodule = "Deathcounter"
                                        functionname = "dead"
                                        cooldown_time = 10

                                        Deathcounter.dead(APICalls.channel_game())

                                if enabled("Raffles"):
                                    if ("!raffle" in messagelow[0:7] or "!giveaway" in messagelow[0:9]) and ismod:
                                        custommodule = "Raffles"
                                        functionname = "raffle"
                                        cooldown_time = 5

                                        Raffles.func_raffle(message)

                                    elif "!join" in messagelow[0:5]:
                                        custommodule = "Raffles"
                                        Raffles.join_raffle(userid, username, message, issub, ismod)

                                if enabled("Roulette"):
                                    if "!roulette" in messagelow[0:9] and not oncooldown("Roulette", "roulette"):
                                        custommodule = "Roulette"
                                        functionname = "roulette"
                                        cooldown_time = 20

                                        Roulette.roulette(username)

                                if enabled("Paddle"):
                                    if "!paddle" in messagelow[0:7] and not oncooldown("Paddle", "paddle"):
                                        custommodule = "Paddle"

                                        cooldown_time = 20
                                        functionname = "paddle"
                                        Paddle.paddle(username, message)

                                if enabled("Quotes"):
                                    if "!lastquote" in messagelow[0:10] and (not oncooldown("Quotes", "last_quote") or ismod):
                                        custommodule = "Quotes"
                                        functionname = "last_quote"
                                        cooldown_time = 0

                                        Quotes.last_quote()

                                    elif "!quote" in messagelow[0:6] and (not oncooldown("Quotes", "quote") or ismod):
                                        custommodule = "Quotes"
                                        functionname = "quote"
                                        cooldown_time = 0

                                        Quotes.quote(message, APICalls.channel_game())

                                if enabled("Backseatmessage"):
                                    if ("!backseatmessage" in messagelow[0:16] or '!bsm' in messagelow[0:4]) and ismod:
                                        Backseatmessage.backseatmessage(message)

                                if enabled("BrokenBoner"):
                                    if "!bet" in messagelow[0:4] or "!bets" in messagelow[0:5]:
                                        custommodule = "BrokenBoner"
                                        BrokenBoner.bet(username, userid, message, ismod)

                                    elif "!currentboner" in messagelow[0:13] and not oncooldown("BrokenBoner", "currentboner"):
                                        custommodule = "BrokenBoner"
                                        functionname = "currentboner"
                                        cooldown_time = 30
                                        BrokenBoner.currentboner()

                                    elif "!brokenboner" in messagelow[0:12] and not oncooldown("BrokenBoner", "brokenboner"):
                                        custommodule = "BrokenBoner"
                                        functionname = "brokenboner"
                                        cooldown_time = 30
                                        BrokenBoner.brokenboner()

                                    elif "!setboner" in messagelow[0:9] and ismod:
                                        BrokenBoner.setboner(message)

                                    elif "!timer" in messagelow[0:6] and (not oncooldown("BrokenBoner", "timer") or ismod):
                                        custommodule = "BrokenBoner"
                                        functionname = "timer"
                                        cooldown_time = 30
                                        BrokenBoner.timer(message, ismod)

                                    elif "!fidwins" in messagelow[0:8] and ismod:
                                        custommodule = "BrokenBoner"
                                        BrokenBoner.fidwins()

                                    elif "!winner" in messagelow[0:7] and ismod:
                                        custommodule = "BrokenBoner"
                                        BrokenBoner.winner(message)

                                if enabled("Questions"):
                                    if "!question" in messagelow[0:9] and not oncooldown("Questions", "question"):
                                        custommodule = "Questions"
                                        functionname = "question"
                                        cooldown_time = Questions.question(message, ismod)

                                if "!bot" in messagelow[0:4]:
                                    Sendmessage.send_message("This bot is made by Bastixx669. "
                                                             "Github: https://github.com/bastixx/ModularBot")

                                if enabled("Conversions"):
                                    if "!convert" in messagelow[0:8] and not oncooldown("Conversions", "convert"):
                                        custommodule = "Conversions"
                                        functionname = "convert"
                                        cooldown_time = 5
                                        Conversions.convert(message)

                                if enabled("RimworldModLinker"):
                                    if "!linkmod" in messagelow[0:8] and not oncooldown("RimworldModLinker", "linkmod"):
                                        custommodule = "RimworldModLinker"
                                        functionname = "linkmod"
                                        cooldown_time = 15

                                        RimworldModLinker.linkmod(message)

                                if enabled("RimworldAutomessage"):
                                    if "!rimworldmessage" in messagelow[0:15]:
                                        custommodule = "RimworldAutomessage"
                                        functionname = "setmessage"
                                        RimworldAutomessage.setmessage(message)

                                if enabled("SongSuggestions"):
                                    if "!suggest" in messagelow[0:8] and (not oncooldown("SongSuggestions", "suggest")or ismod):
                                        custommodule = "SongSuggestions"
                                        functionname = "suggest"
                                        cooldown_time = 5

                                        SongSuggestions.suggest(message)

                                    elif "!clearsuggestions" in messagelow[0:17] and ismod:
                                        custommodule = "SongSuggestions"
                                        SongSuggestions.clearsuggestions()

                                if enabled("CustomCommands"):
                                    if "!command" in messagelow[0:8] and ismod:
                                        custommodule = "CustomCommands"
                                        CustomCommands.func_command(message)

                                if "!module" in messagelow[0:7] and username == 'bastixx669':
                                    arguments = message.split(" ")
                                    if arguments[1] == "enable":
                                        try:
                                            Database.updateone("Modules", {"name": arguments[1]}, {"enabled": True}, True)
                                            Sendmessage.send_message(f"Module {arguments[1]} enabled.")
                                        except:
                                            logger.exception("Error enabling module")
                                            Sendmessage.send_message("Error enabling this module!")
                                    elif arguments[1] == "disable":
                                        try:
                                            Database.updateone("Modules", {"name": arguments[1]}, {"enabled": False}, True)
                                            Sendmessage.send_message(f"Module {arguments[1]} disabled.")
                                        except:
                                            logger.exception("Error enabling module")
                                            Sendmessage.send_message("Error disabling this module!")

                                else:
                                    CustomCommands.check_command(messagelow, username)

                            except:
                                logger.exception(message)
                                Sendmessage.send_message("There was an error with the command. "
                                                         "Please check your command and try again.")
                            finally:
                                if cooldown_time != 0:
                                    # tempdict = {custommodule: {"functions": {functionname: {"next use": time.time() + cooldown_time}}}}
                                    modules[custommodule]["functions"][functionname] = {"next use": time.time() + cooldown_time}
                                    # modules.update(tempdict)
                        else:
                            if enabled('ResponseParse') and msgtype == "PRIVMSG":
                                responseParse.parse_response(message)

                    for l in parts:
                        if "End of /NAMES list" in l:
                            modt = True
                            logger.info(f'Bot ready in channel {CHANNEL.decode()}')
                            modulelist = []
                            for custommodule in modules.keys():
                                if modules[custommodule]["enabled"]:
                                    modulelist.append(custommodule)
                            logger.info(f'Modules loaded: {", ".join(modulelist)}')
                            boottime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            try:
                                if pipe.poll():
                                    controllercommand = pipe.recv()
                                    if controllercommand == "boottime":
                                        pipe.send(boottime)
                            except:
                                logger.exception('Multiprocessing')

        except Exception as errormsg:
            # Disabled due to testing purposes.
            # try:
            #     Errorlog.errorlog(errormsg, 'Main()', temp)
            # except Exception:
            #     Errorlog.errorlog(errormsg, 'Main()', '')
            logging.exception("An exception occured!")
            raise errormsg


# todo add cache for follows
# todo rework bonertimer module
# todo streamline functions/names

if __name__ == '__main__':
    botinstance("27499886", "bastixx669", "")
