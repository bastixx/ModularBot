import random
import time

from Required.Errorlog import errorlog
from Required.Sendmessage import send_message
from Required.Database import *


def load_quotes(FOLDER):
    global folder
    global quotes

    folder = FOLDER
    quotes = {}
    try:
        for document in getallfromdb("Quotes"):
            quotes[document["_id"]] = f'{document["quote"]} - {document["said_by"]} [{document["game"]}] ' \
                                      f'[{document["date"]}]'
    except Exception as errormsg:
        quotes = {}
        errorlog(errormsg, "Quotes/loadquotes()", quotes)


def quote(message, game):
    global quotes
    arguments = message.split(" ")
    try:
        if arguments[1].lower() == "list":
            send_message(f"Quotelist can be found here: http://www.bastixx.nl/twitch/{folder}/quotes.php")
        elif arguments[1].lower() == "add":
            try:
                currentdate = time.strftime("%d/%m/%Y")

                newquote = " ".join(arguments[2:])
                quotes[str(len(quotes) + 1)] = newquote + " [%s] [%s]" % (game, currentdate)
                insertoneindb("Quotes", {"_id": (len(quotes)), "quote": newquote, "game": game, "date": currentdate})
                send_message("Quote %d added!" % len(quotes))
            except Exception as errormsg:
                send_message("There was an error adding this quote. Please try again!")
                errorlog(errormsg, "Quotes/addquote()", message)
        elif arguments[1].lower() == "remove":
            try:
                quotestemp = {}
                del quotes[arguments[2]]
                for key, value in quotes.items():
                    if key > arguments[2]:
                        quotestemp[(key - 1)] = value

                clearcollection("Tempquotes")
                for key, val in quotestemp:
                    quote, game, date = val.split(" [")
                    game = game.rstrip("]")
                    date = date.rstrip("]")

                    insertoneindb("Tempquotes", {"_id": val, "quote": quote, "game": game, "date": date})

                clearcollection("Quotes")
                copycollection("Tempquotes", "Quotes")
                quotes = quotestemp
                send_message("Quote %s removed!" % arguments[2])

            except Exception as errormsg:
                errorlog(errormsg, "Quotes/removequote()", message)
                send_message("There was an error removing this quote. Please ask Bastixx to check!")
        else:
            try:
                if quotes:
                    try:
                        quoteindex = arguments[1]
                        try:
                            int(quoteindex) / 1
                            quote = quotes[quoteindex]
                            send_message("Quote %s: %s" % (quoteindex, quote))
                        except:
                            quotes_temp = {}
                            for key, value in quotes.items():
                                if arguments[1].lower() in value.lower():
                                    quotes_temp[key] = value
                            if len(quotes_temp) == 0:
                                send_message("No quotes found.")
                            elif len(quotes_temp) == 1:
                                for key, value in quotes_temp.items():
                                    send_message("Quote %s: %s" % (key, value))
                            else:
                                keylist = []
                                for key in quotes_temp:
                                    keylist.append(key)
                                randomindex = random.choice(keylist)
                                randomquote = quotes_temp[str(randomindex)]
                                send_message("Quote %s: %s" % (randomindex, randomquote))
                    except KeyError:
                        send_message("This quote does not exist.")
                    except Exception as errormsg:
                        errorlog(errormsg, "Quotes/quote()", message)
                        send_message("Something went wrong, check your command.")
                else:
                    send_message("No quotes yet!")
            except IndexError:
                send_message("Error finding your searchterms. Check your command.")
            except Exception as errormsg:
                errorlog(errormsg, "Quotes/quote()", message)
                send_message("Something went wrong, check your command.")
    except:
        randomindex = random.randint(1, len(quotes))
        randomquote = quotes[str(randomindex)]
        send_message("Quote %s: %s" % (randomindex, randomquote))


def last_quote():
    try:
        quoteindex = len(quotes)
        quote = quotes[str(quoteindex)]
        send_message("Quote %s: %s" % (quoteindex, quote))
    except Exception as errormsg:
        errorlog(errormsg, "Quotes/lastquote()", "")
        send_message("There was an error retrieving the last quote. Error logged.")
