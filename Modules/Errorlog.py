from datetime import datetime
import os


def load_errorlog(FOLDER):
    global folder
    folder = FOLDER
    if not os.path.isdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog'):
        os.mkdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog')


def errorlog(error, functionname, message):
    now = datetime.date(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")

    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog/Errorlog.txt', 'a+') as f:
        f.write(f"{now} : {functionname} : {error} : {message}\n")

    print(f"{now} : {error} : {functionname} : {message}")
