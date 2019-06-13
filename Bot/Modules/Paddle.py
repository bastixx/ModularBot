import random
import logging

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errors import InsufficientParameterException

logger = logging.getLogger(__name__)


def paddle(username, message):
    try:
        messagesplit = message.split(" ")
        if len(messagesplit) != 2:
            raise InsufficientParameterException
        randint = random.randint(1, 20)
        if randint == 1:
            send_message("/timeout %s 5 Get paddled!" % messagesplit[1])
            send_message("%s got paddled so hard by %s they need a few seconds to recover..." %
                         (messagesplit[1].strip("@"), username))
        else:
            send_message("%s gets a paddling from %s! andyt90bat" %
                         (messagesplit[1].strip("@"), username))
    except InsufficientParameterException:
        send_message("Usage: !paddle <username>")
    except:
        logger.exception(f'message: {message}')
        send_message("Something went wrong. Please check your command and try again.")
