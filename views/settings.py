import discord
import datetime
from db_actions import *
import random

# All the buttons and modals for the /settings command

# Modal for configuring settings which require input 
class UserSettingsModal(discord.ui.Modal):
    bet_input = discord.ui.TextInput(label = " ")
    def __init__(self, modalType, default, otherValue, created_at):
        self.modalType = modalType
        if self.modalType == "minTicTacToe":
            title = "Configure Minimum Tic Tac Toe Bet"
            self.bet_input.placeholder = "0"
            self.bet_input.label =  "Minimum Bet amount\n(0 for no minimum bet)"
        else:
            title = "Configure Maximum Tic Tac Toe Bet"
            self.bet_input.placeholder = "100"
            self.bet_input.label =  "Maximum Bet amount\n(0 for no maximum bet)"
        super().__init__(title=title)
        self.bet_input.default = default
        self.newValue = None # Value inputted by user
        self.changeAllowed = None
        self.otherValue = otherValue # The value of the other setting (i.e. if selected setting is Minimum Tic Tac Toe bet, this will be the maximum bet for the user)
        self.created_at = created_at
    async def on_submit(self, interaction: discord.Interaction):
        if datetime.datetime.utcnow().timestamp() - self.created_at >= 60: # Checks if interaction is timed out
            return await interaction.response.send_message("Sorry, the interaction has timed out. Please run the `/settings` command again.", ephemeral=True)
        try:
            self.newValue = int(self.bet_input.value)
            if self.newValue < 0:
                self.changeAllowed = False
                return await interaction.response.send_message("It must be a positive number!", ephemeral = True)
            if self.newValue == self.bet_input.default:
                self.changeAllowed = False
                return await interaction.response.send_message("The number that you entered is already set for that setting!", ephemeral = True)
            if self.newValue != 0:
                if self.modalType == "maxTicTacToe":
                    if self.otherValue != 0 and self.otherValue > self.newValue:
                        self.changeAllowed = False
                        return await interaction.response.send_message("You need to enter a value that is greater than your current minimum tic tac toe bet!", ephemeral = True)
                    elif self.newValue <= 10:
                        await interaction.response.send_message("We have changed your maximum tic tac toe bet to " + str(self.newValue) + "!\nPlease keep in mind that you have entered a pretty low maximum bet, so many people may not want to play tic tac toe with you!", ephemeral = True)
                    else:
                        await interaction.response.send_message("We have changed your maximum tic tac toe bet to " + str(self.newValue) + "!", ephemeral = True)
                else:
                    if self.otherValue != 0 and self.otherValue < self.newValue:
                        self.changeAllowed = False
                        return await interaction.response.send_message("You need to enter a value that is less than your current maximum tic tac toe bet!", ephemeral = True)
                    if self.newValue >= 40:
                        await interaction.response.send_message("We have changed your minimum tic tac toe bet to " + str(self.newValue) + "!\nPlease keep in mind that you have entered a pretty high minimum bet, so many won't be rich enough to play tic tac toe with you!", ephemeral = True)
                    else:
                        await interaction.response.send_message("We have changed your minimum tic tac toe bet to " + str(self.newValue) + "!", ephemeral = True)
                self.changeAllowed = True
            else:
                if self.modalType == "minTicTacToe":
                    await interaction.response.send_message("You now have no minimum bet!", ephemeral = True)
                else:
                    await interaction.response.send_message("You now have no maximum bet!", ephemeral = True)
                self.changeAllowed = True
                self.newValue = None
        except ValueError:
            await interaction.response.send_message("That is not a valid number!", ephemeral=True)
            self.changeAllowed = False
        self.stop()

# Button which triggers the modal
class UserSettingsModalButton(discord.ui.Button):
    def __init__(self, label, style, disabled, row, modalType, default, otherValue, created_at):
        super().__init__(label=label, style=style, disabled=disabled, row=row)
        self.modalType = modalType
        self.default = default
        self.otherValue = otherValue
        self.created_at = created_at
    async def callback(self, interaction: discord.Interaction):
        modal = UserSettingsModal(self.modalType, self.default, self.otherValue, self.created_at)
        await interaction.response.send_modal(modal)
        await modal.wait()
        view: UserSettings = self.view
        changeSetting(interaction.user.id, view.chosen, view.newValue)
        hex_number = random.randint(0,16777215)
        tttenabled = False
        userSettings = getSettings(interaction.user.id)
        embed = discord.Embed(title= interaction.user.name + "'s User Settings", color=hex_number, description = "These are your current user settings. You can change them using the dropdown menu.")
        embed.add_field(name = "Hangman Buttons", value = "Using buttons instead of the text based system when playing a hangman game\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
        embed.add_field(name = "Tic Tac Toe", value = "Allows you to play tic tac toe using `/tictactoe` against other users that also have this settings enabled\n\nCurrent Value: `" + str(userSettings["ticTacToe"]) + "`")
        if userSettings["ticTacToe"]:
            tttenabled = True
            embed.add_field(name = "Minimum Tic Tac Toe bet", value = "Sets the minimum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["minTicTacToe"]) + "`")
            embed.add_field(name = "Maximum Tic Tac Toe bet", value = "Sets the maximum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["maxTicTacToe"]) + "`")
        view.stop()
        view = UserSettings(interaction.user, tttenabled, getSettings(interaction.user.id))
        await interaction.edit_original_response(embed=embed, view=view)

# Buttons for enabling/disabling a setting (which don't require input) and for quitting the interaction
class UserSettingsButton(discord.ui.Button):
    def __init__(self, label, style, disabled, row):
        super().__init__(label=label, style=style, disabled=disabled, row=row)
    async def callback(self, interaction: discord.Interaction):
        view: UserSettings = self.view
        if self.label == "Enable":
            view.newValue = True
            await interaction.response.send_message("That setting has been enabled!", ephemeral=True)
        elif self.label == "Disable":
            view.newValue = False
            await interaction.response.send_message("That setting has been disabled!", ephemeral=True)
        else: # Quit button
            await interaction.response.edit_message(view=None)
            view.quited = True
            view.disableAll()
            view.stop()
            return
        changeSetting(interaction.user.id, view.chosen, view.newValue)
        hex_number = random.randint(0,16777215)
        tttenabled = False
        userSettings = getSettings(interaction.user.id)
        embed = discord.Embed(title= interaction.user.name + "'s User Settings", color=hex_number, description = "These are your current user settings. You can change them using the dropdown menu.")
        embed.add_field(name = "Hangman Buttons", value = "Using buttons instead of the text based system when playing a hangman game\n\nCurrent Value: `" + str(userSettings["hangman_buttons"]) + "`")
        embed.add_field(name = "Tic Tac Toe", value = "Allows you to play tic tac toe using `/tictactoe` against other users that also have this settings enabled\n\nCurrent Value: `" + str(userSettings["ticTacToe"]) + "`")
        if userSettings["ticTacToe"]:
            tttenabled = True
            embed.add_field(name = "Minimum Tic Tac Toe bet", value = "Sets the minimum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["minTicTacToe"]) + "`")
            embed.add_field(name = "Maximum Tic Tac Toe bet", value = "Sets the maximum amount someone can bet against you in Tic Tac Toe\n\nCurrent Value: `" + str(userSettings["maxTicTacToe"]) + "`")
        view.stop()
        original_interaction = view.original_interaction
        view = UserSettings(interaction.user, tttenabled, getSettings(interaction.user.id), original_interaction)
        await original_interaction.edit_original_response(embed=embed, view=view)

# Dropdown which displays all the options for selecting the setting, and creates the buttons according to what the user selects
class UserSettingsDropdown(discord.ui.Select):
    def __init__(self, options, currentSettings):
        super().__init__(options=options, placeholder="Select Setting")
        self.currentSettings = currentSettings
        self.created_at = datetime.datetime.utcnow().timestamp()
    async def callback(self, interaction: discord.Interaction):
        view: UserSettings = self.view
        view.clearButtons()
        view.chosen = self.values[0]
        if view.chosen == "hangman_buttons" or view.chosen == "ticTacToe":
            view.add_item(UserSettingsButton(label="Enable", style = discord.ButtonStyle.green, disabled = self.currentSettings[view.chosen], row=1))
            view.add_item(UserSettingsButton(label="Disable", style = discord.ButtonStyle.red, disabled = not self.currentSettings[view.chosen], row=1))
            view.add_item(UserSettingsButton(label="Quit", style = discord.ButtonStyle.blurple, disabled = False, row=1))
        else:
            default = self.currentSettings[view.chosen]
            if default is None:
                default = 0
            if view.chosen == "minTicTacToe":
                otherValue = self.currentSettings["maxTicTacToe"]
            else:
                otherValue = self.currentSettings["maxTicTacToe"]
            if otherValue == None:
                otherValue = 0
            view.add_item(UserSettingsModalButton(label="Change Limit", style = discord.ButtonStyle.grey, disabled = False, row=1, modalType = view.chosen, default=str(default), otherValue=otherValue, created_at=self.created_at))
            view.add_item(UserSettingsButton(label="Quit", style = discord.ButtonStyle.blurple, disabled = False, row=1))
        for option in self.options:
            if option.value == view.chosen:
                self.placeholder = option.label
                break
        await interaction.response.edit_message(view=view)

# The main view for the interaction, which initially contains only the dropdown and the quit button.
class UserSettings(discord.ui.View):
    def __init__(self, user, tttenabled: bool, currentSettings, original_interaction: discord.Interaction):
        super().__init__()
        self.user = user
        self.original_interaction = original_interaction
        options = [
            discord.SelectOption(label="Hangman Buttons", value = "hangman_buttons", description="Select to configure your setting for hangman buttons!"),
            discord.SelectOption(label="Tic Tac Toe", value = "ticTacToe", description="Select to configure your setting allowing Tic Tac Toe!")
        ]
        if tttenabled:
            options.append(discord.SelectOption(label="Minimum Tic Tac Toe bet", value = "minTicTacToe", description="Select to configure your setting for your minimum Tic Tac Toe bet!"))
            options.append(discord.SelectOption(label="Maximum Tic Tac Toe bet", value = "maxTicTacToe", description="Select to configure your setting for your maximum Tic Tac Toe bet!"))
        self.add_item(UserSettingsDropdown(options, currentSettings))
        self.add_item(UserSettingsButton(label="Quit", style = discord.ButtonStyle.blurple, disabled = False, row=1))
        self.chosen = None
        self.newValue = None
        self.quited = False
        self.changeAllowed = None
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True
        
    def disableAll(self):
        for item in self.children:
            if item.row == 1 and item.label != "Quit":
                self.remove_item(item)
            else:
                item.disabled = True
    def clearButtons(self):
        for item in self.children:
            if item.row == 1:
                self.remove_item(item)