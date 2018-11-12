from datetime import datetime
import os


def load_errorlog(FOLDER):
    global folder
    folder = FOLDER
    if not os.path.isdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog'):
        os.mkdir(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog')


def errorlog(error, functionname, message):
    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog/Errorlog.txt', 'a+') as f:
        f.write(f"{datetime.date(datetime.now())} : {datetime.time(datetime.now())} : {functionname} : {error} : {message}\n")

    print(f"{datetime.date(datetime.now())} : {datetime.time(datetime.now())} : {error} : {functionname} : {message}")
