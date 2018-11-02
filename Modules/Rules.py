from Errorlog import errorlog
from Send_message import send_message
import os


def load_rules(folder):
    rules = {}
    warnings = {}
    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Rules.txt') as f:
        for line in f:
            split = line.split(":")
            rules[split[0]] = {"rule": split[1], "1": split[2], "2": split[3], "3": split[4].strip("\n")}
    return rules, warnings


def func_rules(s, warnings, rules, message):
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
        send_message(s, "/timeout %s %s broke rule %s (%s warning)" % (
            arguments[2], timeouttime, ruleno, warningnotext))
        send_message(s, "@%s You have been timed out for %s seconds because "
                        "you broke rule %s: %s."" This was your %s warning!" %
                     (arguments[2], timeouttime, ruleno, ruletext, warningnotext))
    else:
        send_message(s, "/ban %s  broke rule %s" % (arguments[2], ruleno))
        send_message(s, "@%s You have been banned from this channel because "
                        "you broke rule %s: %s. This was your %s warning!" %
                     (arguments[2], ruleno, ruletext, warningnotext))
