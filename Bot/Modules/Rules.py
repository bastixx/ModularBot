import logging

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database

logger = logging.getLogger(__name__)


def load_rules():
    global rules; global warnings
    rules = {}
    warnings = {}
    try:
        for document in Database.getall("Rules"):
            rules[document["id"]] = {"rule": document["Rule"], "1": document["first_timeout"],
                                     "2": document["second_timeout"], "3": document["third_timeout"]}

    except:
        logger.exception('')
        send_message('Error loading module "Rules". Module disabled.')
        return False


def func_rules(message):
    try:
        arguments = message.split(" ")
        ruleno = arguments[1]
        ruletext = rules[ruleno]['rule']

        if arguments[2] in warnings.keys():
            warningno = str(warnings[arguments[2]].count(ruleno) + 1)
            warnings[arguments[2]].append(ruleno)
        else:
            warnings[arguments[2]] = ruleno
            warningno = '1'

        if warningno == "1":
            warningnotext = "first"
        elif warningno == "2":
            warningnotext = "second"
        elif warningno == "3":
            warningnotext = "third"
        else:
            warningnotext = "null"

        timeouttime = rules[ruleno][warningno]
        if timeouttime != '0':
            send_message(f"/timeout {arguments[2]} {timeouttime} broke rule {ruleno} ({warningnotext} warning)")
            send_message(f"@{arguments[2]} You have been timed out for {timeouttime} seconds because "
                        f"you broke rule {ruleno}: {ruletext}. This was your {warningnotext} warning!")
        else:
            send_message(f"/ban {arguments[2]} broke rule {ruleno}. Total warnings: {warningno}")
            send_message(f"@{arguments[2]} You have been banned from this channel because "
                         f"you broke rule {ruleno}: {ruletext}.")
    except:
        logger.exception(f'message: {message}')
