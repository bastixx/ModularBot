from Bot import instance
import multiprocessing as mp
import logging
import sys
import threading
import queue

bots = dict()
TIMEOUT = 60


def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while True:
        input_str = input()
        inputQueue.put(input_str)


def botStop(bot):
    bot['pipe'] = None
    bot['process'].terminate()
    if bot['process'].join(TIMEOUT) is None:
        print("Bot seems to still be alive after %s seconds.." % TIMEOUT)
        bot['process'].kill()
    bot['process'] = None
    return bot


def botStart(bot, name):
    parent, child = mp.Pipe()
    bot['pipe'] = parent
    process = mp.Process(target=instance, args=[bot["Name"], child], name=name)
    bot['process'] = process
    process.start()
    return bot


def aliveCheck(bots, key):
    proc = bots[key].get('process', None)
    if proc is not None:
        alive = proc.is_alive()
        return not alive
    return False


def pipeCheck(bots, key):
    proc = bots[key].get('pipe', None)
    if proc is not None:
        return proc.poll()
    return False


def boottimeCheck(bot):
    proc = bots[bot].get('pipe', None)
    if proc is not None:
        proc.send("boottime")
        return proc.recv()
    return None


if __name__ == '__main__':
    # mp.set_start_method('spawn')
    # Get botlist from database
    botlist = ("bastixx669",)

    logger = mp.log_to_stderr()
    logger.setLevel(logging.INFO)

    for element in botlist:
        bots[element] = dict(Name=element)
    for name in bots.keys():
        bots[name] = botStart(bots[name], name)

    helpDict = {
        "add": "Adds another bot to the Database, requires a given name",  # Not Implemented
        "exit": "Closes all bots and exits the controller",
        "help": "Displays commandlist or if command given details on the command",
        "lastChat": "Displays the last Chat received by the given Bot to check continued connection to twitch",
    # Commented out -> Bewaren?
        "remove": "Removes bot from the Bot database",  # Not Implemented
        "start": "Starts bot with given name",
        "status": "Displays Status of the given bot",
        "stop": "Stops bot with given name"}

    EXIT_COMMAND = "exit"
    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
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
                            bots[x] = botStop(bots[x], x)
                            bots[x] = botStart(bots[x], x)
                    else:
                        bots[lsplit[1]] = botStop(bots[lsplit[1]], lsplit[1])
                        bots[lsplit[1]] = botStart(bots[lsplit[1]], lsplit[1])

            elif 'stop' in input_str[:5]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Stop requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x] = botStop(bots[x])
                    else:
                        bots[lsplit[1]] = botStop(bots[lsplit[1]])

            elif 'start' in input_str[:6]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                    print("Start requires a valid bot name to be executed.")
                else:
                    if lsplit[1] == 'all':
                        for x in bots.keys():
                            bots[x] = botStart(bots[x], x)
                    else:
                        bots[lsplit[1]] = botStart(bots[lsplit[1]], lsplit[1])

            elif 'help' in input_str[:4]:
                lsplit = input_str.split(" ")
                if len(lsplit) < 2:
                    print("Available commands are: exit, help, lastChat, start, status, stop")
                else:
                    if lsplit[1] in helpDict.keys():
                        print(helpDict[lsplit[1]])
                    else:
                        print("Available commands are: exit, help, lastChat, start, status, stop")

            elif 'status' in input_str[:6]:
                for bot in bots.keys():
                    if bots[bot]["process"] != None:
                        alive = bots[bot]['process'].is_alive()
                        if alive:
                            print("%s: OK" % bot)
                        else:
                            print("%s: Not OK!" % bot)
                        print("%s: Booted on: %s" % (bot, boottimeCheck(bot)))
                    else:
                        print("Bot %s is stopped." % bots[bot]['Name'])

            #             elif 'lastChat' in input_str[:8]:
            #                 lsplit = input_str.split(" ")
            #                 if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
            #                     print("lastChat requires a valid bot name to be executed.")
            #                 else:
            #                     if lsplit[1] == 'all':
            #                         for x in bots.keys():
            #                             bots[x]['pipe'].send("lastChat")
            #                             if bots[x]['pipe'].poll(TIMEOUT):
            #                                 message = bots[x]['pipe'].recv()
            #                                 print("Last message of bot %s recieved on:" + message % bots[x]['ChannelName'])
            #                             else:
            #                                 print("Bot for %s does not answer right now, consider restarting it." % bots[x]['ChannelName'])
            #                     else:
            #                         bots[lsplit[1]]['pipe'].send("lastChat")
            #                         if bots[lsplit[1]]['pipe'].poll(TIMEOUT):
            #                             message = bots[lsplit[1]]['pipe'].recv()
            #                             print("Last message of bot %s recieved on:" + message % bots[lsplit[1]]["ChannelName"])
            #                         else:
            #                             print("Bot for %s does not answer right now, consider restarting it." % bots[lsplit[1]]['ChannelName'])

            elif input_str != '':
                print('"%s" is not a recognised command.' % input_str)

        dead = filter(lambda x: aliveCheck(bots, x), bots.keys())
        if dead:
            for name in dead:
                print("Bot for Channel %s has died" % name)
                bots[name] = botStart(bots[name], name)
        piped = filter(lambda x: pipeCheck(bots, x), bots.keys())
        if piped:
            for name in piped:
                print("There is something stuck in the pipe of %s: %s" % (name, bots[name]['pipe'].recv()))

for name in bots.keys():
    botStop(bots[name], name)
sys.exit(0)