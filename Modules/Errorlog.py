from datetime import datetime
import os


def load_errorlog(FOLDER):
    global folder
    folder = FOLDER


def errorlog(error, functionname, message):
    with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/errorlog/Errorlog.txt', 'a+') as f:
        f.write(f"{datetime.date(datetime.now())} : {datetime.time(datetime.now())} : {functionname} : {error} : {message}\n")

    print(f"{datetime.date(datetime.now())} : {datetime.time(datetime.now())} : {functionname} : {error} : {message}")
