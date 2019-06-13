import time
import logging
from pathlib import Path

from Modules.Required.APICalls import get_modroom

logger = logging.getLogger(__name__)


# Try and get the ID for the mod channel. This is used for the moderation log.
def load_modlog(channelname: str) -> bool:
    try:
        global modroom_available
        global modroom_id
        global chatlogpath
        global modlogpath
        modroom_id, modroom_available = get_modroom()
        base_path = Path(__file__).parent
        chatlogpath = (base_path / f'../Data/{channelname}/chatlog-{str(time.strftime("%d-%m-%Y"))}.log').resolve()
        modlogpath = (base_path / f"../Data/{channelname}/modlog.log").resolve()
    except:
        logger.exception(f'channelname: {channelname}')
        return False


def modlog(duration: str, userid: str, username: str, reason="") -> None:
    timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
    duration = int(duration)

    # Mod action logging
    try:
        if duration == 0:
            action = 'banned'
        elif duration <= 5:
            action = 'purged'
        else:
            action = 'timed out'

        # TODO Settle on final format chatlog & modlog.
        with open(chatlogpath, 'a+', encoding='UTF-8') as f:
            f.write(f"{timestamp},MOD-ACTION,Null,{action}: {username}. duration: {duration}. Reason: {reason}")
        
        with open(modlogpath, 'a+', encoding='UTF-8') as f:
            f.write(f"{timestamp},{action},{username},{userid},{reason},{duration}")

        # if modroom_available:
        #     s.send(
        #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
        #         channel_id.encode(), modroom_id.encode(), message.encode()))

    except:
        logger.exception('')


def removedmessage(username: str, userid: str, message: str, reason="") -> None:
    timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))

    try:
        with open(chatlogpath, 'a+', encoding='UTF-8') as f:
            f.write(f"{timestamp},MOD-ACTION,Null,Removed message from: {username}. Message: {removedmessage}")
        
        with open(modlogpath, 'a+', encoding='UTF-8') as f:
            f.write(f"{timestamp},message removed,{username},{userid},{reason},Null")
    except:
        logger.exception(f'message: {message}')
