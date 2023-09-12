from pymongo import MongoClient
import discord
import os
import time
import math

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
        self.levelsCol = self.db.levels

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
            "tips": True,
            "vote_reminders": True,
            "categories": []
        }
        # default values for user settings
        levelsData = {
            "_id": str(userId),
            "level": 0,
            "xp": 0
        }
        # insert data into database
        self.currencyCol.insert_one(userData)
        self.settingsCol.insert_one(settingsData)
        self.levelsCol.insert_one(levelsData)
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

        default_settings = {
            "_id": str(userId),
            "hangman_buttons": False,
            "ticTacToe": True,
            "minTicTacToe": None,
            "maxTicTacToe": None,
            "boost": 0,
            "tips": True,
            "vote_reminders": True,
            "categories": []
        }
        for setting in default_settings:
            if setting not in userData:
                self.settingsCol.update_one({"_id": str(userId)}, {"$set": {setting: default_settings[setting]}}, upsert = True)
        userData = self.settingsCol.find_one({"_id": str(userId)})
        return userData
    
    def getLevels(self, userId: int) -> dict | None:
        """
        Gets the level data for a user.

        userId (int) -- The ID of the user
        """

        userData = self.levelsCol.find_one({"_id": str(userId)})
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
        self.settingsCol.update_one({"_id": str(userId)}, {"$set": {setting: newValue}}, upsert = True)
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
        self.currencyCol.update_one({"_id": str(userId)}, {"$set": {item: newAmt}}, upsert = True)
        return True
    
    def addCategory(self, userId: int, category: str):
        if "categories" not in self.getSettings(userId):
            self.changeSetting(userId, "categories", [category])
        else:
            self.changeSetting(userId, "categories", self.getSettings()["categories"].append(category))

    async def addXp(self, userId: int, xpAmount: int, interaction: discord.Interaction = None):
        # user doesn't have an account
        if not self.userHasAccount(userId):
            return False
        userData = self.levelsCol.find_one({"_id": str(userId)})
        if userData == None:
            userData = {
            "_id": str(userId),
            "level": 0,
            "xp": 0
            }
            self.levelsCol.insert_one(userData)
        newXp = userData["xp"] + xpAmount
        if newXp >= 100:
            newLevel = userData["level"] + math.floor(newXp / 100)
            self.levelsCol.update_one({"_id": str(userId)}, {"$set": {"xp": newXp % 100, "level": newLevel}})
            if newLevel >= 5 and userData["level"] < 5:
                self.changeItem(userId, "saves", 10)
            elif newLevel >= 10 and userData["level"] < 10:
                self.addCategory(userId, "Objects")
            elif newLevel >= 15 and userData["level"] < 15:
                self.changeItem(userId, "coins", 100)
            elif newLevel >= 30 and userData["level"] < 30:
                self.changeItem(userId, "hints", 35)
            elif newLevel >= 50 and userData["level"] < 50:
                self.addCategory(userId, "Animals")
            elif newLevel >= 75 and userData["level"] < 75:
                self.changeItem(userId, "hints", 200)
            elif newLevel >= 100 and userData["level"] < 100:
                self.addCategory(userId, "Countries")
            elif newLevel >= 1000 and userData["level"] < 1000:
                self.changeSetting(interaction.user.id, "boost", time.time() + 2592000)
            if not interaction is None:
                await interaction.followup.send(f"Congrats! You are now level {newLevel}!")
        else:
            self.levelsCol.update_one({"_id": str(userId)}, {"$set": {"xp": newXp % 100}})
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