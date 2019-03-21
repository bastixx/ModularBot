from Errorlog import errorlog
from Database import *
from Sendmessage import send_message


def load_commands():
    global customcommands
    customcommands = {}
    cursor = getallfromdb("CustomCommands")
    for document in cursor:
        customcommands[document["name"]] = document["action"]
    return customcommands


def func_command(message):
    global customcommands
    arguments = message.split(" ")
    if len(arguments) >= 3:
        if arguments[1] == "add":
            newcommandname = arguments[2]
            newcommandaction = " ".join(arguments[3:])
            customcommands[newcommandname] = newcommandaction
            insertoneindb("CustomCommands", {"name": newcommandname, "action": newcommandaction})
            send_message(f"Command {newcommandname} added!")
        elif arguments[1] == "remove":
            commandname = arguments[2]
            customcommands.remove(commandname)
            deleteoneindb("CustomCommands", {"name": commandname})
            send_message(f"Command {commandname} removed!")
        elif arguments[1] == "edit":
            commandname = arguments[2]
            newcommandaction = " ".join(arguments[3:])
            if commandname in customcommands.keys():
                customcommands[commandname] = newcommandaction
                updateoneindb("CustomCommands", {"name": commandname}, {"action": newcommandaction})
                send_message(f"Command {commandname} updated!")
            else:
                send_message(f"Command {commandname} does not exist!")
    else:
        send_message("Invalid format. Use !command (add|edit|remove) !commandname commandaction.")


def eval_command(message):
    arguments = message.split(" ")
    commandname = arguments[0]
    commandaction = customcommands[commandname]
    send_message(commandaction)

# todo add custom variables
# mapping these as keys with their python variable counterpart
# eg: {"$user": "username"}
