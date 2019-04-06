import random
import os

from Required.Errorlog import errorlog
from Required.Sendmessage import send_message
import Required.Database as Database


def load_questions(FOLDER):
    global questions
    global folder
    folder = FOLDER
    questions = {}
    try:
        if Database.collectionexists("Questions"):
            for document in Database.getallfromdb("Questions"):
                questions[document["_id"]] = document["question"]

        # with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt', 'r') as f:
        #     for line in f:
        #         split = line.split(":")
        #         questions[split[0]] = split[1].rstrip('\n')
    except Exception as errormsg:
        errorlog(errormsg, "Questions/Load_questions()", "")
        # with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Questions.txt', 'w'):
        #     pass


def question(message):
    try:
        if questions:
            randomindex = random.randint(1, len(questions))
            randomquestion = questions[str(randomindex)]
            send_message("%s: %s" % (randomindex, randomquestion))
        else:
            send_message("No questions yet!")
    except Exception as errormsg:
        errorlog(errormsg, "Question/question()", message)
        send_message("Something went wrong, check your command.")


def add_question(message):
    global questions
    created = False
    try:
        keyword = "!addquestion "
        newquestion = message[message.index(keyword) + len(keyword):]
        for i in range(1, len(questions)):
            if i not in questions.keys():
                questions[i] = newquestion
                Database.insertoneindb("Questions", {"_id": i, "question": newquestion})
                created = True
        if not created:
            questions[str(len(questions) + 1)] = newquestion
            Database.insertoneindb("Questions", {"_id": len(questions), "question": newquestion})
        send_message("question %d added!" % len(questions))
    except Exception as errormsg:
        send_message("There was an error adding this question. Please try again!")
        errorlog(errormsg, "Questions/add_question()", message)


def remove_question(message):
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
        send_message("Question %s removed!" % messageparts[1])

    except KeyError:
        send_message(f'Question number {messageparts[1]} does not exist.')

    except Exception as errormsg:
        errorlog(errormsg, "Questions/remove_question()", message)
