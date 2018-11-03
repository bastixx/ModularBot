import random
import time
import os

from Send_message import send_message
from Errorlog import errorlog


def load_quotes(FOLDER):
    global folder
    global quotes

    folder = FOLDER
    quotes = {}
    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'r') as f:
            for line in f:
                split = line.split(":")
                quotes[split[0]] = split[1].rstrip('\n')
    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Quotes.txt', 'w'):
            pass


def get_quote(s, message):
    try:
        if quotes:
            if message == "!quote":
                randomindex = random.randint(1, len(quotes))
                randomquote = quotes[str(randomindex)]
                send_message(s, "Quote %s: %s" % (randomindex, randomquote))

            elif "!quote" in message:
                quotesplit = message.split(" ")
                argument = quotesplit[1]
                if argument == "list":
                    send_message(s, f"Quotelist can be found here: http://bastixx.nl/{folder}/files/quotes")
                else:
                    try:
                        int(argument)
                        quoteindex = message.split(" ")[1]
                        quote = quotes[quoteindex]
                        send_message(s, "Quote %s: %s" % (quoteindex, quote))
                    except KeyError:
                        send_message(s, "This quote does not exist.")
                    except ValueError:
                        quotes_temp = {}
                        for key, value in quotes.items():
                            if argument.lower() in value.lower():
                                quotes_temp[key] = value
                        if len(quotes_temp) == 0:
                            send_message(s, "No quotes found.")
                        elif len(quotes_temp) == 1:
                            for key, value in quotes_temp.items():
                                send_message(s, "Quote %s: %s" % (key, value))
                        else:
                            keylist = []
                            for key in quotes_temp:
                                keylist.append(key)

                            randomindex = random.choice(keylist)
                            randomquote = quotes_temp[str(randomindex)]
                            send_message(s, "Quote %s: %s" % (randomindex, randomquote))
                    except Exception as errormsg:
                        errorlog(errormsg, "Quotes/quote()", message)
                        send_message(s, "Something went wrong, check your command.")
        else:
            send_message(s, "No quotes yet!")


    except IndexError:
        send_message(s, "Error finding your searchterms. Check your command.")
    except Exception as errormsg:
        errorlog(errormsg, "Quotes/quote()", message)
        send_message(s, "Something went wrong, check your command.")


def add_quote(s, message, game):
    global quotes
    try:

        currentdate = time.strftime("%d/%m/%Y")

        keyword = "!addquote "
        newquote = message[message.index(keyword) + len(keyword):]
        quotes[str(len(quotes) + 1)] = newquote + " [%s] [%s]" % (game, currentdate)
        with open(f'C:/Users/Bas_v/Dropbox/Python/{folder}/files/Quotes.txt', 'a') as f:
            f.write("%s:%s [%s] [%s]\n" % (len(quotes), newquote, game, currentdate))
        send_message(s, "Quote %d added!" % len(quotes))
    except Exception as errormsg:
        send_message(s, "There was an error adding this quote. Please try again!")
        errorlog(folder, errormsg, "Quotes/addquote()", message)


def remove_quote(s, message):
    global quotes
    try:
        messageparts = message.split(" ")
        del quotes[messageparts[1]]
        counter = 1
        with open(f'C:/Users/Bas_v/Dropbox/Python/{folder}/files/Quotes.txt', 'w') as f:
            for key, val in quotes.items():
                f.write("%s:%s\n" % (counter, val))
                counter += 1
        quotes = {}
        with open(f'C:/Users/Bas_v/Dropbox/Python/{folder}/files/Quotes.txt') as f:
            for line in f:
                split = line.split(":")
                quotes[split[0]] = split[1].rstrip('\n')
        send_message(s, "Quote %s removed!" % messageparts[1])

    except Exception as errormsg:
        errorlog(folder, errormsg, "Quotes/removequote()", message)


def last_quote(s):
    try:
        quoteindex = len(quotes)
        quote = quotes[str(quoteindex)]
        send_message(s, "Quote %s: %s" % (quoteindex, quote))
    except Exception as errormsg:
        errorlog(folder, errormsg, "Quotes/removequote()", "")
        send_message(s, "There was an error retrieving the last quote. Error logged.")
