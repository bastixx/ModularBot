import threading
from datetime import datetime, timedelta
import logging

import Modules.Required.Database as Database
from Modules.Required.Sendmessage import send_message
from Modules.Required.APICalls import channel_is_live

logger = logging.getLogger(__name__)


def load_commands():
    try:
        global customcommands
        global timer
        customcommands = {}
        cursor = Database.getall("CustomCommands")
        for document in cursor:
            customcommands[document["name"]] = {"action": document["action"], "timer": document["timer"]}
        
        timer = threading.Timer(60, check_timed_commands).start
        check_timed_commands()  # Testing purposes.
        return True
    except:
        logger.exception('Error loading Module. Module disabled.')
        return False


def func_command(message):
    global customcommands
    arguments = message.split(" ")

    try:
        if len(arguments) >= 3:
            if arguments[1] == "add":
                try:
                    newcommandname = arguments[2]
                    newcommandaction = " ".join(arguments[3:])
                    customcommands[newcommandname] = {"action": newcommandaction, "timer": 0}
                    Database.insertone("CustomCommands", {"name": newcommandname, "action": newcommandaction, "timer": 0})
                    send_message(f"Command {newcommandname} added!")
                except:
                    send_message("Something went wrong. Please check your command and try again.")
                    logger.exception(f'message: {message}')

            elif arguments[1] == "remove":
                commandname = arguments[2]
                customcommands.remove(commandname)  # TODO This does not work.
                Database.deleteone("CustomCommands", {"name": commandname})
                send_message(f"Command {commandname} removed!")

            elif arguments[1] == "edit":
                commandname = arguments[2]
                newcommandaction = " ".join(arguments[3:])
                if commandname in customcommands.keys():
                    # !command edit !testcommand timer 60
                    if arguments[3] == "timer":
                        if int(arguments[4]) < 120:
                            send_message("Minimum time is 120 seconds (2 minutes).")
                        else:
                            customcommands[commandname]["timer"] = int(arguments[4])
                            Database.updateone("CustomCommands", {"name": commandname}, {"timer": int(arguments[4])})
                    else:
                        if len(arguments) > 4:
                            customcommands[commandname] = newcommandaction
                            Database.updateone("CustomCommands", {"name": commandname}, {"action": newcommandaction})
                    send_message(f"Command {commandname} updated!")
                else:
                    send_message(f"Command {commandname} does not exist!")
        else:
            send_message("Invalid format. Use !command (add|edit|remove) !commandname commandaction.")
    except:
        logger.exception(f"message: {message}")


def check_command(message, username):
    try:
        global variabledict
        variabledict = dict()
        variabledict["$user"] = {
            "$user": username
        }
        
        arguments = (message.lower()).split(" ")
        if arguments[0] in customcommands.keys():
            
            response = customcommands[arguments[0]]["action"]
            response = replace_variables(response)
            send_message(response)
    except:
        logger.exception(f'message: {message}')


def replace_variables(command):
    try:
        global variabledict
        for variable in variabledict.keys():
            if variable in command:
                command.replace(variable, variabledict[variable])
        return command
    except:
        logger.exception(f'command: {command}')


def check_timed_commands():
    try:
        if not channel_is_live():
            return
        
        for command in customcommands.keys():
            if customcommands[command]["timer"] != 0:
                if customcommands[command].get("last_runtime", None) < (datetime.now() - timedelta(seconds=customcommands[command]["timer"])):
                    send_message(customcommands[command]["action"])
                    customcommands[command]["last_runtime"] = datetime.now()
                    return
                
        timer.start()
    except:
        logger.exception('')
