from ModularBot import botinstance
from Modules.Required import Database as database
import multiprocessing as mp
import sys

bots = dict()
TIMEOUT = 60

helpDict = {
    "add": "Adds another bot to the Database, requires a given name",
    "exit": "Closes all bots and exits the controller",
    "help": "Displays Commandlist or if command given details on the command",
    "lastChat": "Displays the last Chat received by the given Bot to check continued connection to twitch",
    "remove": "Removes bot from the Bot Database",
    "start": "Starts bot with given name", "status": "Displays Status of the given bot",
    "stop": "Stops the given bot"}


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


    while True:
        dead = filter(lambda x: aliveCheck(bots, x), bots.keys())
        if dead:
            for name in dead:
                print("Bot for Channel %s has died" % name)
                bots[name].update(instance=botStart(bots[name], name))
        piped = filter(lambda x: pipeCheck(bots, x), bots.keys())
        if piped:
            for name in piped:
                print("There is something stuck in the pipe of %s: %s" % (name, bots[name]['pipe'].recv()))
        try:
            # Makes the > sign appear in front of the input, indicating something can be entered.
            print(">", end='', flush=True)
            line = sys.stdin.readline().rstrip("\n")
        except KeyboardInterrupt:
            break

        if 'exit' in line[:4]:
            break

        elif 'restart' in line[:7]:
            lsplit = line.split(" ")
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

        elif 'stop' in line[:5]:
            lsplit = line.split(" ")
            if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("Stop requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots[x]["instance"] = botStop(bots[x]["instance"], x)
                else:
                    bots[lsplit[1]]["instance"] = botStop(bots[lsplit[1]]["instance"], lsplit[1])

        elif 'start' in line[:6]:
            lsplit = line.split(" ")
            if len(lsplit) < 2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("Start requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots[x]["instance"] = botStart(bots[x]["instance"], x)
                else:
                    bots[lsplit[1]]["instance"] = botStart(bots[lsplit[1]]["instance"], lsplit[1])

        elif 'help' in line[:4]:
            lsplit = line.split(" ")
            if len(lsplit) < 2:
                print("Available commands are: add, exit, help, lastChat, remove, start, status, stop")
            else:
                if lsplit[1] in helpDict.keys():
                    print(helpDict[lsplit[1]])
                else:
                    print("Available commands are: add, exit, help, lastChat, remove, start, status, stop")

        elif 'lastChat' in line[:8]:
            lsplit = line.split(" ")
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
        else:
            print('"%s" is not a recognised command.' % line)


for name in bots.keys():
    botStop(bots[name]["instance"], name)
sys.exit(0)

