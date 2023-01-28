import time
import math
import discord
from discord import app_commands
from discord.ext import commands
import random
from views.settings import *
from bot import HangmanBot

# Settings Command
class SettingsCog(commands.Cog):
    def __init__(self, bot: HangmanBot):
        self.bot = bot

    async def cog_load(self):
        print("Settings command loaded!")

    @app_commands.command(description = "Configure your user settings")
    async def settings(self, interaction: discord.Interaction):
        userSettings = self.bot.db.getSettings(interaction.user.id)
        if not userSettings:
            return await interaction.response.send_message("You don't have an account yet! Create one using `/create-account`")
        hex_number = random.randint(0,16777215)
        tttenabled = False
        embed = discord.Embed(title= interaction.user.name + "'s User Settings", color=hex_number, description = "These are your current user settings. You can change them using the dropdown menu.")
        embed.add_field(name = "Tips", value = "Periodically send helpful tips about the bot and some new features\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
        embed.add_field(name = "Hangman Buttons", value = "Using buttons instead of the text based system when playing a hangman game\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
        embed.add_field(name = "Tic Tac Toe", value = "Allows you to play tic tac toe using `/tictactoe` against other users that also have this settings enabled\n\nCurrent Value: `" + str(userSettings["ticTacToe"]) + "`")
        if userSettings["ticTacToe"]:
            tttenabled = True
            embed.add_field(name = "Minimum Tic Tac Toe bet", value = "Sets the minimum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["minTicTacToe"]) + "`")
            embed.add_field(name = "Maximum Tic Tac Toe bet", value = "Sets the maximum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["maxTicTacToe"]) + "`")
        view = UserSettings(interaction.user, tttenabled, self.bot.db.getSettings(interaction.user.id), interaction)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="boost-status", description="Check how long you have in left in your boost, if you bought one.")
    async def boost_status(self, interaction: discord.Interaction):
        userSettings = self.bot.db.getSettings(interaction.user.id)
        if(time.time() - userSettings["boost"] >= 3600):
            return await interaction.response.send_message("You don\'t have a currently have a boost. See more information about boosts by using `/shop`.")
        print(int(time.time() - userSettings["boost"]))
        minutes = math.floor((3600 - int(time.time() - userSettings["boost"])) / 60)
        seconds = (3600 - int(time.time() - userSettings["boost"])) % 60
        await interaction.response.send_message(f"You have {minutes} minutes and {seconds} seconds left in your boost!")

async def setup(bot):
    await bot.add_cog(SettingsCog(bot=bot))