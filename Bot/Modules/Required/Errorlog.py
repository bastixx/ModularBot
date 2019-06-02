from datetime import datetime
import json
from pathlib import Path


def load_errorlog(folder):
    global file_path
    base_path = Path(__file__).parent
    file_path = (base_path / f"../../Data/{folder}_errorlog.txt").resolve()


def errorlog(error: Exception, functionname: str, message: str):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(file_path, 'a+') as f:
        f.write(f"timestamp: {now}, error: {str(error)}, function: {functionname}, message: {message}\n")
    print(f"Error: {now} : {str(error)} : {functionname} : {message}")
