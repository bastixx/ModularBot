import os

from Send_message import send_message
from Errorlog import errorlog


def load_suggestions(FOLDER):
    global folder
    folder = FOLDER


def suggest(s, message):
    try:
        keyword = "!suggest "
        suggestion = message[message.index(keyword) + len(keyword):]
        wrongchars = ['<', '>', '{', '}', '(', ')', '#', '%', '*', '\:', "\"", "|"]
        for elem in wrongchars:
            if elem in suggestion:
                suggestion = suggestion.replace(elem, "")

        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/SongSuggestions.txt', 'a') as f:
            f.write(suggestion + "\n")
        send_message(s, "Song suggestion registered!")
    except Exception as errormsg:
        send_message(s, "There was an error adding this. Please try again!")
        errorlog(errormsg, "SongSuggestions/suggest()", message)


def clearsuggestions(s):
    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/SongSuggestions.txt', 'w') as f:
            f.write("")
        send_message(s, "List cleared!")
    except Exception as errormsg:
        send_message(s, "There was an error adding this. Please try again!")
        errorlog(errormsg, "SongSuggestions/clearsuggestions()", "")
