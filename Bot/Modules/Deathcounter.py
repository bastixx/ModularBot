import logging

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database

logger = logging.getLogger(__name__)


def load_deaths():
    global deaths
    deaths = {}

    try:
        for document in Database.getall("Deathcounter"):
            deaths[document["game"]] = document["deaths"]
    except:
        logger.exception('')
        return False


def func_deaths(message, game, ismod):
    arguments = message.split(" ")
    cooldown_time = 0
    skipdb = False

    try:
        if len(arguments) > 3 and arguments[1] in ['add', 'set', 'remove']:
            game = " ".join(arguments[3:]).lower()
        if arguments[1] == "list":
            send_message(f'Current games are: {", ".join(list(deaths.keys()))}')
            cooldown_time = 10
        elif arguments[1] == "add" and ismod:
            if game in deaths:
                deaths[game] += int(arguments[2])
            else:
                deaths[game] = int(arguments[2])
            send_message(f"New death counter for {game} is now: {deaths[game]}")
            cooldown_time = 5
        elif arguments[1] == "set" and ismod:
            deaths[game] = int(arguments[2])
            send_message(f"Deaths for {game} set to {deaths[game]}")
            cooldown_time = 5
        elif arguments[1] == "remove" and ismod:
            if deaths[game] - int(arguments[2]) < 0:
                send_message(f"Deaths can't be negative. Current deaths: {deaths[game]}")
            elif game in deaths:
                deaths[game] -= int(arguments[2])
                send_message(f"New death counter for {game} is now: {deaths[game]}")
            else:
                send_message(f"There are no deaths (yet) for {game}")
            cooldown_time = 5
        elif " ".join(arguments[1:]).lower() in deaths:
            game = " ".join(arguments[1:]).lower()
            send_message(f"Deaths in {game}: {deaths[game]}!")
            cooldown_time = 20
        else:
            send_message(f'Command \"!deaths { " ".join(arguments[1:])}\" not recognised or '
                         "no deaths yet for this game.")
            cooldown_time = 10

    except IndexError:
        if game in deaths:
            send_message(f"Deaths in {game}: {deaths[game]}!")
        else:
            send_message(f"There are no deaths (yet) for {game}")
            skipdb = True
        cooldown_time = 20
    except KeyError:
        send_message(f"There are no deaths (yet) for {game}")
        cooldown_time = 20
    except:
        logger.exception(f'message: {message}')
        send_message("Something went wrong. Please check your command.")
        cooldown_time = 5

    finally:
        if not skipdb:
            Database.updateone("Deaths", {"game": game}, {"game": game, "deaths": deaths[game]}, True)
        return cooldown_time


def dead(game):
    try:
        if game in deaths:
            deaths[game] += 1
        else:
            deaths[game] = 1
        send_message(f"A new death! Deathcount: {deaths[game]}!")
        Database.updateone("Deaths", {"game": game}, {"game": game, "deaths": deaths[game]}, True)
    except:
        send_message("A error occured. Please try again.")
        logger.exception(f'game: {game}')
