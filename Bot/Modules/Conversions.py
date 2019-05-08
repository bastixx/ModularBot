import re
import math

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message

patterns = {
    "Feet & inches": {"pattern": "([0-9,\.]+ ?)(?:ft|\') ?([0-9,\.]+ ?)(?:in|\'\')", "function": "convert_feetandinches"},
    "Feet": {"pattern": "([0-9,\.]+ ?)(?:ft|')", "function": "convert_feet"},
    "Inches": {"pattern": "([0-9,\.]+ ?)in", "function": "convert_inches"},
    "Centimetres": {"pattern": "([0-9,\.]+ ?)cm", "function": "convert_centimetres"},
    "Stone": {"pattern": "([0-9,\.]+ ?)lb", "function": "convert_stone"},
    "Kilograms": {"pattern": "([0-9,\.]+ ?)kg", "function": "convert_kilogram"},
    "Miles": {"pattern": "([0-9,\.]+ ?)mi", "function": "convert_miles"},
    "Kilometres": {"pattern": "([0-9,\.]+ ?)km", "function": "convert_kilometres"},
    "Fahrenheit": {"pattern": "(-?[0-9,\.]+ ?)°?f", "function": "convert_fahrenheit"},
    "Celsius": {"pattern": "(-?[0-9,\.]+ ?)°?c", "function": "convert_celsius"},
    "Kelvin": {"pattern": "(-?[0-9,\.]+ ?)°?k", "function": "convert_kelvin"}
}

for pattern in patterns:
    patterns[pattern] = re.compile(patterns[pattern])

def convert(message):
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.I)
        if match:
            patterns[pattern]["function"](match)
            return
    # If there is no match:
    send_message("Unable to convert this. Unknown format or typo. "
         "Supported formats are: "
         "Mi, KM, °F, °C, °K, KG, lb, cm, ft and in.")

def convert_feetandinches(match):
    feet, inches = float(match.group(1)), float(match.group(2))
    cm = (feet * 30.48) + (inches * 2.54)
    send_message(f"{feet} ft and {inches} in is {round(cm, 2)} cm!")

def convert_feet(match):
    feet = float(match.group(1))
    cm = (feet * 30.48)
    send_message(f"{feet} ft is {round(cm, 2)} cm!")

def convert_inches(match):
    inch = float(match.group(1))
    cm = (inch * 2.54)
    send_message(f"{inch} in is {round(cm, 2)} cm!")

def convert_centimetres(match):
    cm = float(match.group(1))
    tempinches, feet = math.modf(cm * 0.03281)
    inches = tempinches * 12
    send_message(f"{cm} cm is {int(feet)}ft {round(inches, 1)}in!")

def convert_stone(match):
    lb = float(match.group(1))
    kg = lb * 0.45359237
    send_message(f"{lb} lb is {round(kg, 2)} kg!")

def convert_kilogram(match):
    kg = float(match.group(1))
    lb = kg / 0.45359237
    send_message(f"{kg} kg is {round(lb, 2)} lb!")

def convert_miles(match):
    kilometres = float(match.group(1))
    miles = kilometres * 1.609344
    send_message(f"{kilometres} km is {round(miles, 2)} mi!")

def convert_kilometres(match):
    miles = float(match.group(1))
    kilometres = miles / 1.609344
    send_message(f"{miles} mi is {round(kilometres, 2)} km!")

def convert_fahrenheit(match):
    fahrenheit = float(match.group(1))
    celsius = (fahrenheit - 32) / 1.8
    send_message(f"{fahrenheit} °F is {round(celsius, 2)} °C!")

def convert_celsius(match):
    celsius = float(match.group(1))
    fahrenheit = (celsius * 1.8) + 32
    send_message(f"{celsius} °C is {round(fahrenheit, 2)} °F!")

def convert_kelvin(match):
    kelvin = float(match.group(1))
    celsius = kelvin - 273.15
    send_message(f"{kelvin} °K is {round(celsius, 2)} °C!")
