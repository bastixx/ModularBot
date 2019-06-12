import json
from Modules.Required.Errorlog import errorlog
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.ERROR)
fh = logging.FileHandler(filename="Log.log", mode="a+")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
                              datefmt='%d-%b-%y %H:%M:%S')

sh.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)


def load_database(database):
    global db
    global channel
    global logger
    channel = database
    try:
        base_path = Path(__file__).parent
        file_path = (base_path / f"../../Data/{database}.json").resolve()
        with open(file_path) as f:
            db = json.load(f)
    except:
        logger.exception(f"Database: {database}")


def write_to_file():
    try:
        with open(f"/home/pi/ModularBot/Bot/Data/{channel}.json", 'w') as f:
            json.dump(db, f, indent=4)
    except:
        logger.exception(f"Error writing to db file {channel}: ")


def getchannel():
    return channel


# Returns all entries in a collection.
def getall(collection: str) -> dict:
    try:
        return db[collection]
    except:
        logger.exception(f"Collection: {collection}")


# Returns the first entry matching the filter.
# The dbfilter argument needs to be a dict with a single key-value pair.
def getone(collection: str, dbfilter={}) -> dict:
    try:
        for item in db[collection]:
            if dbfilter == {}:
                return item
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    return item
        return {}
    except:
        logger.exception(f"Collection: {collection}")


# Inserts an entry into the specified collection.
def insertone(collection: str, data: dict):
    global db
    try:
        # TODO add check if entry is unique?
        db[collection].append(data)
        write_to_file()
    except:
        logger.exception(f"Collection: {collection}")


# Removes first occurence of an entry matching the filter.
# The dbfilter argument needs to be a dict with a single key-value pair.
def deleteone(collection: str, dbfilter: dict):
    global db
    try:
        for item in db[collection]:
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    db[collection].remove(item)
    except:
        logger.exception(f"Collection: {collection}, Filter: {str(dbfilter)}")


# Deletes a collection from the database.
def deletecollection(collection: str):
    global db
    try:
        del db[collection]
    except:
        logger.exception(f"Collection: {collection}")


# Updates the first entry in the collection with new values based on a filter.
# Optional flag to create the entry if it does not exist -> CURRENTLY UNUSED!
# The dbfilter argument needs to be a dict with a single key-value pair.
def updateone(collection: str, dbfilter: dict, data: dict, create=False):
    global db
    try:
        for item in db[collection]:
            for key, value in item.items():
                if dbfilter == {}:
                    db[collection][db[collection].index(item)].update(data)
                    write_to_file()
                    return
                if item[key] == dbfilter.get(key, None):
                    db[collection][db[collection].index(item)].update(data)
                    write_to_file()
                    return
    except:
        logger.exception(f"Collection: {collection}, Filter: {str(dbfilter)}, Data: {str(data)}")


# Updates many entries in the collection with new values based on a filter.
# The dbfilter argument needs to be a dict with a single key-value pair.
def updatemany(collection: str, dbfilter: dict, data: dict):
    global db
    try:
        for item in db[collection]:
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    db[collection][item].update(data)
        write_to_file()
    except:
        logger.exception(f"Collection: {collection}, Filter: {str(dbfilter)}, Data: {str(data)}")


# Clears a collection of all entries.
def clearcollection(collection: str):
    global db
    try:
        db[collection] = []
        write_to_file()
    except:
        logger.exception(f"Collection: {collection}")


# Makes a copy from the specified colletion.
def copycollection(oldcollection: str, newcollection: str):
    global db
    try:
        db[newcollection] = list(db[oldcollection])
        write_to_file()
    except:
        logger.exception(f"Oldcollection: {oldcollection}, Newcollection: {newcollection}")


# Check if a collection exists.
def collectionexists(collection: str):
    try:
        if collection in db.keys():
            return True
        else:
            return False
    except:
        logger.exception(f"Collection: {collection}")
