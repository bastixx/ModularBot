from Required.Errorlog import errorlog
from Required.Sendmessage import send_message
from Required.Database import *

global responsedict
responsedict = dict()


def loadResponses(FOLDER):
    global responsedict
    try:
        for document in getallfromdb("Quotes"):
            responsedict.update(document["phrase"]=document["response"])
    except Exception as errormsg:
        errorlog(errormsg, "responseParse/loadResponses", responsedict)
        responsedict=dict()

def parseResponse(chat):
    for x in responsedict.keys():
        if x in chat:
            send_message(responsedict[x])
