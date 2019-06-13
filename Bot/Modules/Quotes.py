import random
import time
import logging

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database

logger = logging.getLogger(__name__)


def load_quotes():
    global quotes
    global channel
    channel = Database.getchannel()
    quotes = {}
    try:
        for document in Database.getall("Quotes"):
            quotes[document["id"]] = {"quote": document["quote"], "said_by": document["said_by"], "game": document["game"], "date": document["date"]}

    except:
        logger.exception('')
        return False


def quote(message, game):
    global quotes
    arguments = message.split(" ")
    if len(arguments) == 1:
        randomindex = random.randint(1, len(quotes))
        randomquote = quotes[randomindex]
        send_message(f"Quote {randomindex}: {randomquote['quote']} - {randomquote['said_by']} [{randomquote['game']}] "
                     f"[{randomquote['date']}]")
    else:
        if arguments[1].lower() == "list":
            send_message(f"Quotelist can be found here: http://www.bastixx.nl/twitch/{channel}/quotes.php")
        elif arguments[1].lower() == "add":
            try:
                currentdate = time.strftime("%d/%m/%Y")

                newquote = " ".join(arguments[2:])
                newquote, said_by = newquote.split("-")
                quotes[len(quotes) + 1] = {"quote": newquote, "said_by": said_by, "game": game, "date": currentdate}
                Database.insertone("Quotes", {"id": len(quotes), "quote": newquote, "said_by": said_by, "game": game,
                                              "date": currentdate})
                send_message("Quote %d added!" % len(quotes))
            except ValueError:
                send_message("There was an error adding this quote."
                             "Make sure the quote is in the format: \"Quote\" - username!")
            except:
                send_message("There was an error adding this quote. Please check your command and try again.")
                logger.exception(f"message: {message}")

        elif arguments[1].lower() == "edit":
            # !quote edit 25 newquote - user
            try:
                newquote = " ".join(arguments[3:])
                newquote, said_by = newquote.split("-")
                quotes[int(arguments[2])]["quote"] = newquote
                quotes[int(arguments[2])]["said_by"] = said_by
                Database.updateone("Quotes", {"id": arguments[2]}, {"quote": newquote, "said_by": said_by})
                send_message(f"Quote {arguments[2]} updated!")
            except:
                send_message("There was an error editing this quote. Please try again.")
                logger.exception(f"message: {message}")
        
        elif arguments[1].lower() == "remove":
            try:
                quotestemp = {}
                del quotes[int(arguments[2])]
                for key, value in quotes.items():
                    if key < int(arguments[2]):
                        quotestemp[key] = value
                    else:
                        quotestemp[(key - 1)] = value

                for key, val in quotestemp.items():
                    Database.insertone("Tempquotes", {"id": key, "quote": val['quote'], "said_by": val['said_by'],
                                                      "game": val['game'], "date": val['date']})

                Database.clearcollection("Quotes")
                Database.copycollection("Tempquotes", "Quotes")
                Database.clearcollection("Tempquotes")
                quotes = quotestemp
                send_message("Quote %s removed!" % arguments[2])

            except:
                logger.exception(f"message: {message}")
                send_message("There was an error removing this quote. Please try again.")
        else:
            try:
                if quotes:
                    try:
                        quoteindex = arguments[1]
                        try:
                            int(quoteindex) / 1
                            quote = quotes[int(quoteindex)]
                            send_message(f"Quote {quoteindex}: {quote['quote']} - {quote['said_by']} [{quote['game']}] "
                                         f"[{quote['date']}]")
                        except:
                            quotes_temp = {}
                            for key, value in quotes.items():
                                if arguments[1].lower() in value['quote'].lower():
                                    quotes_temp[key] = value
                            if len(quotes_temp) == 0:
                                send_message("No quotes found.")
                            elif len(quotes_temp) == 1:
                                for key, value in quotes_temp.items():
                                    send_message(
                                        f"Quote {key}: {value['quote']} - {value['said_by']} [{value['game']}] "
                                        f"[{value['date']}]")
                            else:
                                keylist = []
                                for key in quotes_temp:
                                    keylist.append(key)
                                randomindex = random.choice(keylist)
                                randomquote = quotes_temp[randomindex]
                                send_message(f"Quote {quoteindex}: {randomquote['quote']} - {randomquote['said_by']} "
                                             f"[{randomquote['game']}] [{randomquote['date']}]")
                    except KeyError:
                        send_message("This quote does not exist.")
                    except Exception as errormsg:
                        errorlog(errormsg, "Quotes/quote()", message)
                        send_message("Something went wrong, check your command.")
                else:
                    send_message("No quotes yet!")
            except IndexError:
                send_message("Error finding your searchterms. Check your command.")
            except:
                logger.exception(f"message: {message}")
                send_message("Something went wrong, check your command.")


def last_quote():
    try:
        quoteindex = len(quotes)
        quote = quotes[quoteindex]
        send_message(f"Quote {quoteindex}: {quote['quote']} - {quote['said_by']} [{quote['game']}] "
                     f"[{quote['date']}]")
    except:
        logger.exception("")
        send_message("There was an error retrieving the last quote. Error logged.")
