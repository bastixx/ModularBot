import logging 

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database

logger = logging.getLogger(__name__)


def load_responses():
    global responsedict
    responsedict = {}
    try:
        for document in Database.getall("Responses"):
            responsedict[document["phrase"]] = document["response"]
        return True
    except:
        logger.exception('Error loading Module. Module disabled.')
        return False


def parse_response(chat):
    try: 
        for x in responsedict.keys():
            if x in chat:
                send_message(responsedict[x])
    except:
        logger.exception(f'chat: {chat}')
