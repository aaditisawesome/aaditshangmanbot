import discord
from discord import app_commands
from discord.ext import commands
from db_actions import *
import random
from views.settings import *

# Settings Command
class SettingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print("Settings command loaded!")

    @app_commands.command(description = "Configure your user settings")
    async def settings(self, interaction: discord.Interaction):
        userSettings = getSettings(interaction.user.id)
        if not userSettings:
            return await interaction.response.send_message("You don't have an account yet! Create one using `/create-account`")
        hex_number = random.randint(0,16777215)
        tttenabled = False
        embed = discord.Embed(title= interaction.user.name + "'s User Settings", color=hex_number, description = "These are your current user settings. You can change them using the dropdown menu.")
        embed.add_field(name = "Hangman Buttons", value = "Using buttons instead of the text based system when playing a hangman game\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
        embed.add_field(name = "Tic Tac Toe", value = "Allows you to play tic tac toe using `/tictactoe` against other users that also have this settings enabled\n\nCurrent Value: `" + str(userSettings["ticTacToe"]) + "`")
        if userSettings["ticTacToe"]:
            tttenabled = True
            embed.add_field(name = "Minimum Tic Tac Toe bet", value = "Sets the minimum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["minTicTacToe"]) + "`")
            embed.add_field(name = "Maximum Tic Tac Toe bet", value = "Sets the maximum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["maxTicTacToe"]) + "`")
        view = UserSettings(interaction.user, tttenabled, getSettings(interaction.user.id))
        await interaction.response.send_message(embed=embed, view=view)
        while True:
            timed_out = await view.wait()
            if timed_out:
                view.disableAll()
                return await interaction.edit_original_response(content = "Interaction timed out...", view=view)
            if view.quited:
                return
            if view.changeAllowed:
                changeSetting(interaction.user.id, view.chosen, view.newValue)
                tttenabled = False
                userSettings = getSettings(interaction.user.id)
                embed.clear_fields()
                embed.add_field(name = "Hangman Buttons", value = "Using buttons instead of the text based system when playing a hangman game\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
                embed.add_field(name = "Tic Tac Toe", value = "Allows you to play tic tac toe using `/tictactoe` against other users that also have this settings enabled\n\nCurrent Value: `" + str(userSettings["ticTacToe"]) + "`")
                if userSettings["ticTacToe"]:
                    tttenabled = True
                    embed.add_field(name = "Minimum Tic Tac Toe bet", value = "Sets the minimum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["minTicTacToe"]) + "`")
                    embed.add_field(name = "Maximum Tic Tac Toe bet", value = "Sets the maximum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["maxTicTacToe"]) + "`")
            view = UserSettings(interaction.user, tttenabled, getSettings(interaction.user.id))
            await interaction.edit_original_response(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SettingsCog(bot=bot))