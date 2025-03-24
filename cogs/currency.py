import discord
from discord import app_commands
from discord.ext import commands
import time
from bot import HangmanBot

# Commands which are directly related to the currency system (does not include game commands)
class CurrencyCog(commands.Cog):
    def __init__(self, bot: HangmanBot):
        self.bot = bot

    async def cog_load(self):
        print("Currency commands loaded!")

    @app_commands.command(description = "Check how many coins you have!")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.send_message("Counting money...")
        if member != None:
            items = self.bot.db.getItems(member.id)
            if(len(items) > 0):
                await interaction.edit_original_response(content = (member.mention + " has " + items[0] + " coins! \n They also have " + items[1] + " hints and " + items[2] + " saves!"))
            else:
                await interaction.edit_original_response(content = "The specified user doesn't have an account! Tell them to create one using `/create-account`.")
        else:
            items = self.bot.db.getItems(interaction.user.id)
            if(len(items) > 0):
                await interaction.edit_original_response(content = (interaction.user.mention + ", you have " + items[0] + " coins! \n You also have " + items[1] + " hints and " + items[2] + " saves!"))
            else:
                await interaction.edit_original_response(content = "You don't have an account yet! Create one using `/create-account`!")
    
    @app_commands.command(description = "Buy an item from the shop")
    async def buy(self, interaction, item: str, amount : int = 1):
        if item == "hint":
            await interaction.response.send_message("Giving you hint(s)...")
            try:
                transactionWorked = self.bot.db.changeItem(interaction.user.id, "coins", -5 * amount)
                if not transactionWorked:
                    await interaction.edit_original_response(content = "You don't have that many coins (Hints cost 5 coins each)! Get coins by winning hangman games `/start`! (If you haven't created an account, create one with `/create-account`).")
                    return
                self.bot.db.changeItem(interaction.user.id, "hints", amount)
                await interaction.edit_original_response(content = "Success! You now have " + str(amount) + " more hint(s).")
            except Exception as e:
                print(e)
        elif item == "boost":
            await interaction.response.send_message("Giving you a boost...")
            try:
                userSettings = self.bot.db.getSettings(interaction.user.id)
                if userSettings["boost"] > time.time():
                    return await interaction.edit_original_response(content = f"You already have a boost running! You can see how much time you have left in it using `/boost-status`.")
                transactionWorked = self.bot.db.changeItem(interaction.user.id, "coins", -15)
                if not transactionWorked:
                    await interaction.edit_original_response(content = "You don't have enough coins (Boosts cost 15 coins each)! Get coins by winning hangman games `/start`! (If you haven't created an account, create one with `/create-account`).")
                    return
                self.bot.db.changeSetting(interaction.user.id, "boost", time.time() + 3600)
                await interaction.edit_original_response(content = "Success! You will now receive 2x coins for 1 hour. You can check how much time you have left in your boost using `/boost-status`!")
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message("That is an invalid item. Please see `/shop`")

    @app_commands.command(description = "If you are rich and your friend is poor, you can give them coins")
    async def pay(self, interaction, member: discord.Member, amount: int):
        await interaction.response.send_message("Paying money...")
        if amount < 0:
            return await interaction.edit_original_response(content="You cannot pay negative coins!")
        transactionWorked = self.bot.db.changeItem(interaction.user.id, "coins", -1 * amount)
        if not transactionWorked:
            await interaction.edit_original_response(content = "You either don't have that many coins, or you don't have an account. Create an account using `/create-account.`")
            return
        transactionWorked = self.bot.db.changeItem(member.id, "coins", amount)
        if not transactionWorked:
            await interaction.edit_original_response(content = "The specified user does not have an account yet. Tell them to create one using `/createaccount`.!")
            self.bot.db.changeItem(interaction.user.id, "coins", amount)
            return   
        await interaction.edit_original_response(content = f"Successfully gave {member.mention} {amount} coins!")

async def setup(bot):
    await bot.add_cog(CurrencyCog(bot=bot))