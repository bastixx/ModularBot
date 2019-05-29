from datetime import datetime
import json


def load_errorlog(FOLDER):
    global folder
    folder = FOLDER


def errorlog(error: Exception, functionname: str, message: str):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(f"../../Data/{folder}_errorlog.json", 'a+') as f:
        json.dump({"timestamp": now, "error": str(error), "function": functionname, "message": message}, f)
    print(f"{now} : {str(error)} : {functionname} : {message}")
