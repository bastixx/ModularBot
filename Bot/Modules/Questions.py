import random
import logging

from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database

logger = logging.getLogger(__name__)


def load_questions():
    global questions
    questions = {}
    try:
        if Database.collectionexists("Questions"):
            for document in Database.getall("Questions"):
                questions[document["id"]] = document["question"]
        return True
    except:
        logger.exception('Error loading Module. Module disabled.')
        return False


def question(message, ismod):
    global questions
    arguments = message.split(" ")
    try:
        if len(arguments) > 1:
            if arguments[1] == "add" and ismod:
                try:
                    newquestion = " ".join(arguments[2:])
                    # Loop over all keys and check if this slot is taken
                    for i in range(1, len(questions)):
                        if i not in questions.keys():
                            questions[i] = newquestion
                            Database.insertone("Questions", {"id": i, "question": newquestion})
                            send_message(f"Question {i} added!")
                            return
                    # If there is no empty gap in the question list:
                    questions[str(len(questions) + 1)] = newquestion
                    Database.insertone("Questions", {"id": len(questions), "question": newquestion})
                    send_message(f"Question {len(questions)} added!")
                except:
                    send_message("There was an error adding this question. Please try again!")
                    logger.exception(f"Command: {message}")
                finally:
                    cooldowntime = 5

            elif arguments[1] == "remove" and ismod:
                try:
                    if questions.get(arguments[2], False):
                        del questions[arguments[2]]
                        Database.deleteone("Questions", {"id": arguments[2]})
                    send_message(f"Question {arguments[2]} removed!")

                except KeyError:
                    send_message(f'Question number {arguments[2]} does not exist.')

                except:
                    logger.exception(f"Command: {message}")
                    send_message("There was an error removing this question. Please check your command and try again.")
                finally:
                    cooldowntime = 5

            elif arguments[1] == "edit" and ismod:
                try:
                    if questions.get(arguments[2], False):
                        newquestion = " ".join(arguments[3:])
                        questions[arguments[2]] = newquestion
                        Database.updateone("Questions", {"id": arguments[2]}, {"question": newquestion})
                        send_message(f"Question {arguments[2]} updated: {newquestion}")
                except:
                    logger.exception(f"Command: {message}")
                    send_message("There was an error editing this question. Please check your command and try again.")
                finally:
                    cooldowntime = 5
            else:
                try:
                    int(arguments[1]) / 1
                    send_message(f"{arguments[1]}: {questions[int(arguments[1])]}")
                    cooldowntime = 20
                except ValueError:
                    send_message("Unrecognized argument. Allowed arguments are: add, remove, edit or a number.")
                    cooldowntime = 5
                except KeyError:
                    send_message(f"question {arguments[1]} does not exist!.")
                    cooldowntime = 5
        else:
            try:
                if questions:
                    randomindex = random.randint(1, len(questions))
                    send_message(f"{randomindex}: {questions[randomindex]}")
                else:
                    send_message("No questions yet!")
            except:
                logger.exception(f"Command: {message}")
                send_message("Something went wrong, check your command.")
            finally:
                cooldowntime = 20
    except:
        logger.exception('')
        send_message('Something went wrong. Please check your command and try again.')
    finally:
        return cooldowntime
