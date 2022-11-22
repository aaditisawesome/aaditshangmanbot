from pymongo import MongoClient
import os

mongo_client = MongoClient(os.environ["MONGO_DB_URL"])
db = mongo_client.hangman
currencyCol = db.currency
settingsCol = db.settings

def changeItem(userId: int, item: str, incrementAmt: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return False
    if userData[item] + incrementAmt < 0:
        return False
    newAmt = userData[item] + incrementAmt
    currencyCol.update_one({"_id": str(userId)}, {"$set": {item: newAmt}})
    return True

def initiateUser(userId: int):
    if userHasAccount(userId):
        return False
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
        "maxTicTacToe": None
    }
    currencyCol.insert_one(userData)
    settingsCol.insert_one(settingsData)
    return True

def deleteUser(userId: int):
    if not userHasAccount(userId):
        return False
    currencyCol.delete_one({"_id": str(userId)})
    return True

def getItems(userId: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return []
    return [str(userData["coins"]), str(userData["hints"]), str(userData["saves"])]

def userHasAccount(userId: int):
    userData = currencyCol.find_one({"_id": str(userId)})
    if userData == None:
        return False
    return True

def getSettings(userId: int):
    userData = settingsCol.find_one({"_id": str(userId)})
    return userData

def changeSetting(userId: int, setting: str, newValue):
    userSettings = settingsCol.find_one({"_id": str(userId)})
    print(userSettings)
    if userSettings == None:
        return False
    settingsCol.update_one({"_id": str(userId)}, {"$set": {setting: newValue}})
    return True

def getRich():
    richUsers = {}
    sortedUsers = currencyCol.find().sort("coins", -1)
    for i in range(5):
        richUsers[sortedUsers[i]["_id"]] = sortedUsers[i]["coins"]
    return richUsers