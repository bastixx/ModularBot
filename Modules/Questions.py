import random
import os

from Errorlog import errorlog
from Send_message import send_message


def load_questions(FOLDER):
    global questions
    global folder
    folder = FOLDER
    questions = {}
    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt') as f:
        for line in f:
            split = line.split(":")
            questions[split[0]] = split[1].rstrip('\n')


def question(s, message):
    try:
        if len(questions) > 0:
            randomindex = random.randint(1, len(questions))
            randomquestion = questions[str(randomindex)]
            send_message(s, "%s: %s" % (randomindex, randomquestion))
        else:
            send_message(s, "No questions yet!")
    except Exception as errormsg:
        errorlog(errormsg, "Question/question()", message)
        send_message(s, "Something went wrong, check your command.")


def add_question(s, message):
    global questions
    try:
        keyword = "!addquestion "
        newquestion = message[message.index(keyword) + len(keyword):]
        questions[str(len(questions) + 1)] = newquestion
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt", 'a') as f:
            f.write("%s:%s\n" % (len(questions), newquestion))
        send_message(s, "question %d added!" % len(questions))
    except Exception as errormsg:
        send_message(s, "There was an error adding this question. Please try again!")
        errorlog(errormsg, "Questions/add_question()", message)


def remove_question(s, message):
    global questions
    try:
        messageparts = message.split(" ")
        del questions[messageparts[1]]
        qcounter = 1
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt", 'w') as f:
            for key, val in questions.items():
                f.write("%s:%s\n" % (qcounter, val))
                qcounter += 1
        questions = {}
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt') as f:
            for line in f:
                split = line.split(":")
                questions[split[0]] = split[1].rstrip('\n')
        send_message(s, "Question %s removed!" % messageparts[1])

    except KeyError:
        send_message(s, f'Question number {messageparts[1]} does not exist.')

    except Exception as errormsg:
        errorlog(errormsg, "Questions/remove_question()", message)
