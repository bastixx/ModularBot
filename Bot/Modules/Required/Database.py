import json
from Modules.Required.Errorlog import errorlog
from pathlib import Path


def load_database(database):
    global db
    global channel
    channel = database
    try:
        base_path = Path(__file__).parent
        file_path = (base_path / f"../../Data/{database}.json").resolve()
        with open(file_path) as f:
            db = json.load(f)
    except Exception as errormsg:
        errorlog(errormsg, "Database/Load_database()", "Error reading JSON file:")


def write_to_file(database):
    try:
        with open(database + ".json", 'w') as f:
            json.dump(database, f)
    except Exception as errormsg:
        errorlog(errormsg, "Database/write_to_file()", f"Error writing to db file {database}: ")


def getchannel():
    return channel


# Returns all entries in a collection.
def getall(collection: str) -> dict:
    try:
        return db[collection]
    except Exception as errormsg:
        errorlog(errormsg, "Database/getall()", f"Collection: {collection}")
        raise Exception


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
    except Exception as errormsg:
        errorlog(errormsg, "Database/getone()", f"Collection: {collection}")
        raise Exception


# Inserts an entry into the specified collection.
def insertone(collection: str, data: dict):
    try:
        # TODO add check if entry is unique?
        db[collection].append(data)
    except Exception as errormsg:
        errorlog(errormsg, "Database/insertone()", "data: " + str(data))
        raise Exception


# Removes first occurence of an entry matching the filter.
# The dbfilter argument needs to be a dict with a single key-value pair.
def deleteone(collection: str, dbfilter: dict):
    try:
        for item in db[collection]:
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    db[collection].remove(item)
    except Exception as errormsg:
        errorlog(errormsg, "Database/deleteone()", "filter: " + str(dbfilter))
        raise Exception


# Deletes a collection from the database.
def deletecollection(collection: str):
    try:
        del db[collection]
    except Exception as errormsg:
        errorlog(errormsg, "Database/deletecollection()", "collection: " + collection)
        raise Exception


# Updates the first entry in the collection with new values based on a filter.
# Optional flag to create the entry if it does not exist -> CURRENTLY UNUSED!
# The dbfilter argument needs to be a dict with a single key-value pair.
def updateone(collection: str, dbfilter: dict, data: dict, create=False):
    try:
        for item in db[collection]:
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    db[collection][item].update(data)
                    return
    except Exception as errormsg:
        errorlog(errormsg, "Database/updateone()", "filter: " + str(dbfilter) + " Data: " + str(data))
        raise Exception


# Updates many entries in the collection with new values based on a filter.
# The dbfilter argument needs to be a dict with a single key-value pair.
def updatemanyindb(collection: str, dbfilter: dict, data: dict):
    try:
        for item in db[collection]:
            for key, value in item.items():
                if item[key] == dbfilter.get(key, None):
                    db[collection][item].update(data)
    except Exception as errormsg:
        errorlog(errormsg, "Database/updatemany()", "filter: " + str(dbfilter) + " Data: " + str(data))
        raise Exception


# Clears a collection of all entries.
def clearcollection(collection: str):
    try:
        db[collection] = []
    except Exception as errormsg:
        errorlog(errormsg, "Database/clearcollection()", collection)
        return Exception


# Makes a copy from the specified colletion.
def copycollection(oldcollection: str, newcollection: str):
    try:
        db[newcollection] = list(db[oldcollection])
    except Exception as errormsg:
        errorlog(errormsg, "Database/clearcollection()", f"old: {oldcollection}, new: {newcollection}")
        return Exception


# Check if a collection exists.
def collectionexists(collection: str):
    try:
        if collection in db.Keys():
            return True
        else:
            return False
    except Exception as errormsg:
        errorlog(errormsg, "Database/doescollectionexitt()", collection)
        return Exception

