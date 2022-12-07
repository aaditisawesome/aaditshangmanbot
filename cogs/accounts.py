import discord
from discord import app_commands
from discord.ext import commands
from db_actions import *
from views.confirmprompt import *

# Commands which involve the hangman accounts and the legal stuff
class AccountsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print("Accounts commands loaded!")

    @app_commands.command()
    async def create_account(self, interaction: discord.Interaction):
        await interaction.response.send_message("Creating account...", ephemeral=True)
        hasAccount = userHasAccount(interaction.user.id)
        if hasAccount:
            return await interaction.edit_original_response(content = "You already have an account!")
        view = ConfirmPrompt(interaction.user)
        await interaction.edit_original_response(content = "Before creating your hangman account, please read our privacy policy and our terms of service at https://github.com/aaditisawesome/aaditshangmanbot/blob/main/README.md. If you agree to the policy and want to proceed with your account creation, click the `Confirm` button below.", view=view)
        await view.wait()
        if view.confirmed == None:
            return await interaction.edit_original_response(content = "Interaction has timed out...", view=None)
        if view.confirmed:
            userInitiated = initiateUser(interaction.user.id)
            if userInitiated == True:
                if interaction.user in self.bot.authors:
                    self.bot.authors.pop(interaction.user)
                return await interaction.edit_original_response(content = "Your account has been created! You can now play hangman using `/start`.", view=None)
            else:
                return await interaction.edit_original_response(content = "You already have an account!", view=None) 
        await interaction.edit_original_response(content = "You have decided not to create an account. Please tell us what you didn't agree with in the privacy policy or ToS in https://discord.gg/CRGE5nF .", view=None)

    @app_commands.command()
    async def delete_account(self, interaction: discord.Interaction):
        await interaction.response.send_message("Deleting account...", ephemeral = True)
        hasAccount = userHasAccount(interaction.user.id)
        if not hasAccount:
            return await interaction.edit_original_response(content = "You don\'t even have an account! Create one using `/create-account`")
        view = ConfirmPrompt(interaction.user)
        await interaction.edit_original_response(content = "Are you sure you want to delete your account? If you delete your account, all of your coins and inventory will be gone, and you will not be able to play a hangman game without creating an account again!", view=view)
        await view.wait()
        if view.confirmed == None:
            return await interaction.edit_original_response(content = "Interaction has timed out...", view=None)
        if view.confirmed:
            userDeleted = deleteUser(interaction.user.id)
            if userDeleted == True:
                if interaction.user in self.bot.authors:
                    self.bot.authors.pop(interaction.user)
                return await interaction.edit_original_response(content = "Your account has been deleted :(. Please tell us why you deleted your account in https://discord.gg/CRGE5nF so that we can improve our bot!", view=None)
            else:
                return await interaction.edit_original_response(content = "You don't even have an account! What do you expect me to delete? Create an account using `/create-account`.", view=None) 
        await interaction.edit_original_response(content = "You have decided not to delete your account. I am proud of you!", view=None)

    @app_commands.command(description = "The bot's privacy policy!")
    async def policy(interaction):
        await interaction.response.send_message("Here is our privacy policy: https://github.com/aaditisawesome/aaditshangmanbot/blob/main/README.md . If you agree to the privacy policy and want to create an account, use `/create-account`.")

async def setup(bot):
    await bot.add_cog(AccountsCog(bot=bot))