from pymongo import MongoClient
import os

mongo_client = MongoClient(os.environ["MONGO_DB_URL"])
db = mongo_client.hangman
currencyCol = db.currency
settingsCol = db.settings

# Functions which help add, change, or delete any values in the database.
# They return True if whatever the function is supposed to do works, and False if it doesn't (i.e. if the user does not 
# have an account or they don't have enough coins).

def changeItem(userId: int, item: str, incrementAmt: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return False # user doesn't have an account
    if userData[item] + incrementAmt < 0:
        return False # The change would result in a negative balance for the user, so it wouldn't work
    newAmt = userData[item] + incrementAmt
    currencyCol.update_one({"_id": str(userId)}, {"$set": {item: newAmt}})
    return True

def initiateUser(userId: int):
    if userHasAccount(userId):
        return False # User already has an account
    userData = {
        "_id": str(userId),
        "coins": 0,
        "hints": 0,
        "saves": 0,
        "defenitions": 0
    }
    settingsData = {
        "_id": str(userId),
        "hangman_buttons": False,
        "ticTacToe": True,
        "minTicTacToe": None,
        "maxTicTacToe": None,
        "boost": 0,
        "tips": True
    }
    currencyCol.insert_one(userData)
    settingsCol.insert_one(settingsData)
    return True

def deleteUser(userId: int):
    if not userHasAccount(userId):
        return False # User doesn't have an account
    currencyCol.delete_one({"_id": str(userId)})
    settingsCol.delete_one({"_id": str(userId)})
    return True

def getItems(userId: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return [] # Returns empty list when user doesn't have an account
    return [str(userData["coins"]), str(userData["hints"]), str(userData["saves"])]

def userHasAccount(userId: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return False # User doesn't have an account
    return True

def getSettings(userId: int):
    userData = settingsCol.find_one({"_id": str(userId)})
    return userData # Will return None if user doesn't have account

def changeSetting(userId: int, setting: str, newValue):
    userSettings = settingsCol.find_one({"_id": str(userId)})
    print(userSettings)
    if userSettings == None:
        return False # User doesn't have account
    settingsCol.update_one({"_id": str(userId)}, {"$set": {setting: newValue}})
    return True

def getRich(): # used for /rich cmd
    richUsers = {}
    sortedUsers = currencyCol.find().sort("coins", -1) # Sort in descending order
    for i in range(5):
        richUsers[sortedUsers[i]["_id"]] = sortedUsers[i]["coins"]
    return richUsers