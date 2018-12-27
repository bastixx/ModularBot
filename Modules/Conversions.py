import re
import math

from Errorlog import errorlog
from Send_message import send_message


def convert(s, message):
    messagesplit = message.split(" ")

    match = re.search('([0-9,\.]+)ft([0-9,\.]+)in', messagesplit[1], flags=re.I) or \
            re.search('([0-9,\.]+)\'([0-9,\.]+)\'\'', messagesplit[1], flags=re.I)
    if match:
        feet, inches = float(match.group(1)), float(match.group(2))
        cm = (feet * 30.48) + (inches * 2.54)
        send_message(s, f"{messagesplit[1]} is {round(cm, 2)} cm!")
    else:
        match = re.search('([0-9,\.]+)ft', messagesplit[1], flags=re.I) or \
                re.search('([0-9,\.]+)\'', messagesplit[1], flags=re.I)
        if match:
            feet = float(match.group(1))
            cm = (feet * 30.48)
            send_message(s, f"{messagesplit[1]} is {round(cm, 2)} cm!")
        else:
            match = re.search('([0-9,\.]+)cm', messagesplit[1], flags=re.I)
            if match:
                cm = float(match.group(1))
                tempinches, feet = math.modf(cm * 0.03281)
                inches = tempinches * 12
                send_message(s, f"{messagesplit[1]} is {int(feet)}ft {round(inches, 1)}in!")
            else:
                match = re.search('([0-9,\.]+)lb', messagesplit[1], flags=re.I)
                if match:
                    lb = float(match.group(1))
                    kg = lb * 0.45359237
                    send_message(s, f"{lb} lb is {round(kg, 2)} kg!")
                else:
                    match = re.search('([0-9,\.]+)kg', messagesplit[1], flags=re.I)
                    if match:
                        kg = float(match.group(1))
                        lb = kg / 0.45359237
                        send_message(s, f"{kg} kg is {round(lb, 2)} lb!")
                    else:
                        match = re.search('([0-9,\.]+)f', messagesplit[1], flags=re.I) or \
                                re.search('([0-9,\.]+)°f', messagesplit[1], flags=re.I)
                        if match:
                            fahrenheit = float(match.group(1))
                            celsius = (fahrenheit - 32) / 1.8
                            send_message(s, f"{fahrenheit} °F is {round(celsius, 2)} °C!")
                        else:
                            match = re.search('([0-9,\.]+)c', messagesplit[1], flags=re.I) or \
                                    re.search('([0-9,\.]+)°c', messagesplit[1], flags=re.I)
                            if match:
                                celsius = float(match.group(1))
                                fahrenheit = (celsius * 1.8) + 32
                                send_message(s, f"{celsius} °C is {round(fahrenheit, 2)} °F!")
                            else:
                                match = re.search('([0-9,\.]+)k', messagesplit[1], flags=re.I)
                                if match:
                                    kelvin = float(match.group(1))
                                    celsius = kelvin - 273.15
                                    send_message(s, f"{kelvin} °K is {round(celsius, 2)} °C!")
