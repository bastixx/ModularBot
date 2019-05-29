from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database


def load_responses():
    global responsedict
    responsedict = {}
    try:
        for document in Database.getall("Responses"):
            responsedict[document["phrase"]] = document["response"]
    except Exception as errormsg:
        errorlog(errormsg, "responseParse/loadResponses", "")
        responsedict = dict()


def parse_response(chat):
    for x in responsedict.keys():
        if x in chat:
            send_message(responsedict[x])
