from ModularBot import botinstance
from Modules.Required import Database as database
import multiprocessing as mp
import sys
import threading
import queue
import logging, logging.config, logging.handlers

bots = dict()
TIMEOUT = 60

loggingconfig = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
            'dateformat': '%d-%b-%y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'Log.log',
            'when': 'd',
            'interval': 1,
            'backupCount': 28
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
}


helpDict = {
    "add": "Adds another bot to thle Database, requires a given name",
    "exit": "Closes all bots and exits the controller",
    "help": "Displays Commandlist or if command given details on the command",
    "lastChat": "Displays the last Chat received by the given Bot to check continued connection to twitch",
    "remove": "Removes bot from the Bot Database",
    "start": "Starts bot with given name",
    "status": "Displays Status of the given bot",
    "stop": "Stops the given bot"}


def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while True:
        input_str = input()
        inputQueue.put(input_str)


def bot_stop(bot):
    bot['pipe'] = None
    bot['process'].terminate()
    bot['process'].join(TIMEOUT)
    bot['process'] = None
    bot["boottime"] = None
    logger.info(f"Bot {bot['ChannelName']} stopped.")
    return bot


def bot_start(bot, name):
    parent, child = mp.Pipe()
    bot['pipe'] = parent
    process = mp.Process(target=botinstance, args=[bot['ChannelId'], bot["ChannelName"], child], name=name)
    bot['process'] = process
    process.start()
    logger.info(f"Bot {name} started.")
    bot["boottime"] = boottime_check(name)
    return bot


def alive_check(bots, key):
    proc = bots[key].get('process', None)
    if proc is not None:
        alive = proc.is_alive()
        return not alive
    return False


def pipe_check(bots, key):
    proc = bots[key].get('pipe', None)
    if proc is not None:
        return proc.poll()
    return False


def boottime_check(bot):
    proc = bots[bot].get('pipe', None)
    if proc is not None:
        proc.send("boottime")
        return proc.recv()
    return None


if __name__ == '__main__':
    logging.config.dictConfig(loggingconfig)
    logger = logging.getLogger('Controller')

    database.load_database("Controller")
    for element in database.getall("Channels"):
        bots[element['name']] = dict(ChannelName=element['name'], ChannelId=element["id"])
    for name in bots.keys():
        bots[name] = bot_start(bots[name], name)

    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=False)
    inputThread.start()
    while True:
        if inputQueue.qsize() > 0:
            input_str = inputQueue.get()

            if 'exit' in input_str[:4]:
                break

            elif 'restart' in input_str[:7]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Restart requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x] = bot_stop(bots[x])
                            bots[x] = bot_start(bots[x], x)
                    else:
                        bots[lsplit[1]] = bot_stop(bots[lsplit[1]])
                        bots[lsplit[1]] = bot_start(bots[lsplit[1]], lsplit[1])

            elif 'stop' in input_str[:5]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Stop requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x] = bot_stop(bots[x])
                    else:
                        bots[lsplit[1]] = bot_stop(bots[lsplit[1]])

            elif 'start' in input_str[:6]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Start requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x] = bot_start(bots[x], x)
                    else:
                        bots[lsplit[1]] = bot_start(bots[lsplit[1]], lsplit[1])

            elif 'help' in input_str[:4]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2:
                    print("Available commands are: add, exit, help, remove, start, status, stop")
                else:
                    if lsplit[1] in helpDict.keys():
                        print(helpDict[lsplit[1]])
                    else:
                        print("Available commands are: add, exit, help, remove, start, status, stop")

            elif 'status' in input_str[:6]:
                for bot in bots.keys():
                    if bots[bot]["process"] is not None:
                        alive = bots[bot]['process'].is_alive()
                        if alive:
                            print(f"{bot}: OK. Booted on: {bots[bot]['boottime']}")
                        else:
                            print(f"{bot}: not OK! Booted on: {bots[bot]['boottime']}")
                    else:
                        print("Bot %s is stopped." % bots[bot]['ChannelName'])

            elif input_str != '':
                print(f'"{input_str}" is not a recognised command.')

        dead = filter(lambda x: alive_check(bots, x), bots.keys())
        if dead:
            for name in dead:
                logger.error(f"Bot for Channel {name} has died")
                bots[name] = bot_start(bots[name], name)
        piped = filter(lambda x: pipe_check(bots, x), bots.keys())
        if piped:
            for name in piped:
                print(f"There is something stuck in the pipe of {name}: {bots[name]['pipe'].recv()}")

for name in bots.keys():
    bot_stop(bots[name])
sys.exit(0)
