from ModularBot import botinstance
from Modules.Required import Database as database
import multiprocessing as mp
import sys
import threading
import queue
import time

bots = dict()
TIMEOUT = 60


helpDict = {
    "add": "Adds another bot to thle Database, requires a given name",
    "exit": "Closes all bots and exits the controller",
    "help": "Displays Commandlist or if command given details on the command",
    "lastChat": "Displays the last Chat received by the given Bot to check continued connection to twitch",
    "remove": "Removes bot from the Bot Database",
    "start": "Starts bot with given name", "status": "Displays Status of the given bot",
    "stop": "Stops the given bot"}


def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while True:
        input_str = input()
        inputQueue.put(input_str)


def botStop(bot, name):
    bot.pop('pipe', None)
    bot['process'].terminate()
    if bot['process'].join(TIMEOUT) is None:
        bot['process'].kill()
    bot.pop('process', None)
    return bot


def botStart(bot, name):
    parent, child = mp.Pipe()
    bot['pipe'] = parent
    process = mp.Process(target=botinstance, args=[bot['ChannelId'], bot["ChannelName"], child], name=name)
    bot['process'] = process
    process.start()
    return bot


def aliveCheck(bots, key):
    proc = bots[key]["instance"].get('process', None)
    if proc is not None:
        return not proc.is_alive()
    return False


def pipeCheck(bots, key):
    proc = bots[key]["instance"].get('pipe', None)
    if proc is not None:
        return proc.poll()
    return False

if __name__ == '__main__':
    mp.set_start_method('spawn')
    database.load_database("Controller")
    for element in database.getallfromdb("ChannelsTest"):
        bots[element['ChannelName']] = dict(ChannelName=element['ChannelName'], ChannelId=element["ChannelId"])
    for name in bots.keys():
        bots[name].update(instance=botStart(bots[name], name))

    EXIT_COMMAND = "exit"
    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()
    while True:
        if inputQueue.qsize() > 0:
            input_str = inputQueue.get()
            # print("input_str = {}".format(input_str))

            if 'exit' in input_str[:4]:
                break

            elif 'restart' in input_str[:7]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Restart requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x].update(instance=botStop(bots[x], x))
                            bots[x].update(instance=botStart(bots[x], x))
                    else:
                        bots[lsplit[1]].update(instance=botStop(bots[lsplit[1]]["instance"], lsplit[1]))
                        bots[lsplit[1]].update(instance=botStart(bots[lsplit[1]]["instance"], lsplit[1]))

            elif 'stop' in input_str[:5]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Stop requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x]["instance"] = botStop(bots[x]["instance"], x)
                    else:
                        bots[lsplit[1]]["instance"] = botStop(bots[lsplit[1]]["instance"], lsplit[1])

            elif 'start' in input_str[:6]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Start requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x]["instance"] = botStart(bots[x]["instance"], x)
                    else:
                        bots[lsplit[1]]["instance"] = botStart(bots[lsplit[1]]["instance"], lsplit[1])

            elif 'help' in input_str[:4]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2:
                    print("Available commands are: add, exit, help, lastChat, remove, start, status, stop")
                else:
                    if lsplit[1] in helpDict.keys():
                        print(helpDict[lsplit[1]])
                    else:
                        print("Available commands are: add, exit, help, lastChat, remove, start, status, stop")

            elif 'lastChat' in input_str[:8]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("lastChat requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x]["instance"]['pipe'].send("lastChat")
                            if bots[x]["instance"]['pipe'].poll(TIMEOUT):
                                message = bots[x]["instance"]['pipe'].recv()
                                print("Last message of bot %s recieved on:" + message % bots[x]['ChannelName'])
                            else:
                                print("Bot for %s does not answer right now, consider restarting it." % bots[x]['ChannelName'])
                    else:
                        bots[lsplit[1]]["instance"]['pipe'].send("lastChat")
                        if bots[lsplit[1]]["instance"]['pipe'].poll(TIMEOUT):
                            message = bots[lsplit[1]]["instance"]['pipe'].recv()
                            print("Last message of bot %s recieved on:" + message % bots[lsplit[1]]["ChannelName"])
                        else:
                            print("Bot for %s does not answer right now, consider restarting it." % bots[lsplit[1]]['ChannelName'])
            elif input_str != '':
                print('"%s" is not a recognised command.' % input_str)

        dead = filter(lambda x: aliveCheck(bots, x), bots.keys())
        if dead:
            for name in dead:
                print("Bot for Channel %s has died" % name)
                bots[name].update(instance=botStart(bots[name], name))
        piped = filter(lambda x: pipeCheck(bots, x), bots.keys())
        if piped:
            for name in piped:
                print("There is something stuck in the pipe of %s: %s" % (name, bots[name]['pipe'].recv()))
        time.sleep(0.01)

for name in bots.keys():
    botStop(bots[name]["instance"], name)
sys.exit(0)

