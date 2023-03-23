from pymongo import MongoClient
import os

# Functions which help add, change, or delete any values in the database.
# They return True if whatever the function is supposed to do works, and False if it doesn't (i.e. if the user does not 
# have an account or they don't have enough coins).

class MongoDB(MongoClient):
    """
    Implements CRUD (create, read, update, delete) functionality for
    MongoDB. Functions return True if execution is successful, and False
    if otherwise (for example, if the user doesn't have an account, or
    they don't have enough coins to complete the transaction)

    Extends pymongo.MongoClient
    """
    def __init__(self):
        # connects to MongoDB
        super().__init__(os.environ["MONGO_DB_URL"])
        # gets database, currency table, and settings table
        self.db = self.hangman
        self.currencyCol = self.db.currency
        self.settingsCol = self.db.settings

    def userHasAccount(self, userId: int) -> bool:
        """
        Checks if the specified user has an account

        userId (int) -- The user's id
        """
        # find a user with specified id
        if(str(userId) in os.environ["blacklisted"]):
            return False
        userData = self.currencyCol.find_one({"_id": str(userId)})
        # if no data exists, return false
        if userData == None:
            return False
        return True
    
    def initiateUser(self, userId: int) -> bool:
        """
        Creates a new account for a user

        userId (int) -- The ID of the user
        """

        # user already has an account
        if self.userHasAccount(userId):
            return False
            
        # initialize values for user data
        userData = {
            "_id": str(userId),
            "coins": 0,
            "hints": 0,
            "saves": 0,
            "defenitions": 0
        }
        # default values for user settings
        settingsData = {
            "_id": str(userId),
            "hangman_buttons": False,
            "ticTacToe": True,
            "minTicTacToe": None,
            "maxTicTacToe": None,
            "boost": 0,
            "tips": True
        }
        # insert data into database
        self.currencyCol.insert_one(userData)
        self.settingsCol.insert_one(settingsData)
        return True

    def getItems(self, userId: int) -> list:
        """
        Gets the amount of each item a user has

        userId (int) -- The ID of the user
        """
        
        userData = self.currencyCol.find_one({"_id": str(userId)})
        if userData == None:
            # returns empty list when user doesn't have an account
            return []
        return [str(userData["coins"]), str(userData["hints"]), str(userData["saves"])]
    
    def getSettings(self, userId: int) -> dict | None:
        """
        Gets the setting states for a user.

        userId (int) -- The ID of the user
        """

        userData = self.settingsCol.find_one({"_id": str(userId)})
        # will return None if user doesn't have account
        return userData
    
    def changeSetting(self, userId: int, setting: str, newValue: bool | float) -> bool:
        """
        Toggles the setting of a user

        userId (int) -- The user's id
        setting (str) -- The setting to change
        """
        # check if user has account
        userSettings = self.settingsCol.find_one({"_id": str(userId)})
        if userSettings == None:
            return False # User doesn't have account
        self.settingsCol.update_one({"_id": str(userId)}, {"$set": {setting: newValue}})
        return True

    def changeItem(self, userId: int, item: str, incrementAmt: int) -> bool:
        """
        Changes the amount of a user's item by a specified amount

        userId (int) -- The ID of the user
        item (str) -- Which item's amount to modify
        incrementAmt (int) -- How much to modify the item's amount by
        """

        userData = self.currencyCol.find_one({"_id": str(userId)})
        # user doesn't have an account
        if userData == None:
            return False
        # change would result in negative amount
        if userData[item] + incrementAmt < 0:
            return False
        newAmt = userData[item] + incrementAmt
        self.currencyCol.update_one({"_id": str(userId)}, {"$set": {item: newAmt}})
        return True

    def deleteUser(self, userId: int) -> bool:
        """
        Deletes a user's account

        userId (int) -- The user's id
        """
        # if the user doesn't have an account, it can't be deleted
        if not self.userHasAccount(userId):
            return False
        # delete user data and settings
        self.currencyCol.delete_one({"_id": str(userId)})
        self.settingsCol.delete_one({"_id": str(userId)})
        return True

    def getRich(self):
        """
        Gets the top 5 richest players in the bot

        Used in the `/rich` command
        """
        richUsers = {}
        # sorts coin amounts in descending order
        sortedUsers = self.currencyCol.find().sort("coins", -1)
        # adds first five users to richUsers, and return it
        for i in range(5):
            richUsers[sortedUsers[i]["_id"]] = sortedUsers[i]["coins"]
        return richUsers