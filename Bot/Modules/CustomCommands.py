from Modules.Required.Errorlog import errorlog
import Modules.Required.Database as Database
from Modules.Required.Sendmessage import send_message


def load_commands():
    global customcommands
    customcommands = {}
    cursor = Database.getallfromdb("CustomCommands")
    for document in cursor:
        customcommands[document["name"]] = document["action"]
        
    variabledict = {
        "$user": ""
    }
    return customcommands


def func_command(message):
    global customcommands
    arguments = message.split(" ")
    
    if len(arguments) >= 3:
        if arguments[1] == "add":
            newcommandname = arguments[2]
            newcommandaction = " ".join(arguments[3:])
            customcommands[newcommandname] = newcommandaction
            Database.insertoneindb("CustomCommands", {"name": newcommandname, "action": newcommandaction})
            send_message(f"Command {newcommandname} added!")
            
        elif arguments[1] == "remove":
            commandname = arguments[2]
            customcommands.remove(commandname)
            Database.deleteoneindb("CustomCommands", {"name": commandname})
            send_message(f"Command {commandname} removed!")
            
        elif arguments[1] == "edit":
            commandname = arguments[2]
            newcommandaction = " ".join(arguments[3:])
            if commandname in customcommands.keys():
                customcommands[commandname] = newcommandaction
                Database.updateoneindb("CustomCommands", {"name": commandname}, {"action": newcommandaction})
                send_message(f"Command {commandname} updated!")
            else:
                send_message(f"Command {commandname} does not exist!")
    else:
        send_message("Invalid format. Use !command (add|edit|remove) !commandname commandaction.")


def check_command(message, username):
    variabledict["$user"] = username
    
    arguments = (message.lower()).split(" ")
    if arguments[0] in customcommands.keys():
        
        response = customcommands[arguments[0]]
        response = replace_variables(response)
        send_message(response)


def replace_variables(command):
    for variable in variabledict.keys():
        if variable in command:
            command.replace(variable, variabledict[variable])
    
# todo add custom variables
# mapping these as keys with their python variable counterpart
# eg: {"$user": "username"}
