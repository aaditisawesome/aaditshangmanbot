from pymongo import MongoClient
import os

mongo_client = MongoClient(os.environ["MONGO_DB_URL"])
db = mongo_client.hangman
collection = db.currency

def changeItem(member, item: str, incrementAmt: int):
    userData = collection.find_one({"_id": str(member.id)})
    if userData == None:
        return False
    if userData[item] + incrementAmt < 0:
        return False
    newAmt = userData[item] + incrementAmt
    collection.update_one({"_id": str(member.id)}, {"$set": {item: newAmt}})
    return True

def initiateUser(interaction):
    userData = {
        "_id": str(interaction.user.id),
        "coins": 0,
        "hints": 0,
        "saves": 0,
        "defenitions": 0
    }
    collection.insert_one(userData)

def deleteUser(interaction):
    userData = collection.find_one({"_id": str(interaction.user.id)})
    if userData == None:
        return False
    collection.delete_one({"_id": str(interaction.user.id)})
    return True

def getItems(member):
    userData = collection.find_one({"_id": str(member.id)})
    if userData == None:
        return []
    return [str(userData["coins"]), str(userData["hints"]), str(userData["saves"])]

def userHasAccount(userId):
    userData = collection.find_one({"_id": str(userId)})
    if userData == None:
        return False
    return True

def getRich():
    richUsers = {}
    sortedUsers = collection.find().sort("coins", -1)
    for i in range(5):
        richUsers[sortedUsers[i]["_id"]] = sortedUsers[i]["coins"]
    return richUsers