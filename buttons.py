import discord
import datetime

# Tic Tac Toe
class TicTacToeButton(discord.ui.Button):
    def __init__(self, row: int, buttonNumber: int):
        super().__init__(style = discord.ButtonStyle.grey, disabled = False, label = "‎", row = row)
        self.author = None
        self.buttonNumber = buttonNumber
    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        self.author = interaction.user
        if view.userAssignments[self.author] == "X":
            emoji = discord.PartialEmoji(name="\U0000274c")
            self.emoji = emoji
            self.label = None
            self.disabled = True
            self.style = discord.ButtonStyle.green
            view.buttonStatus[self.buttonNumber] = "X"
        else:
            emoji = discord.PartialEmoji.from_str("<:green_circle:1041083758377451571>")
            self.emoji = emoji
            self.label = None
            self.disabled = True
            self.style = discord.ButtonStyle.red
            view.buttonStatus[self.buttonNumber] = "O"
        temp = view.turn
        view.turn = view.not_turn
        view.not_turn = temp
        if view.checkWinner() is None:
            if view.checkTie():
                await interaction.response.edit_message(content = "The game is a tie! Both of your coins have remained unchanged.", view=view)
                view.tie = True
                view.stop()
            else:
                await interaction.response.edit_message(content = list(view.userAssignments.keys())[0].mention + " vs " + list(view.userAssignments.keys())[1].mention + ": Tic Tac Toe\n\n" + view.turn.mention + ", it is your turn! You have 1 minute to respond before you automatically lose!" ,view=view)
        else:
            view.winner = list(view.userAssignments.keys())[list(view.userAssignments.values()).index(view.checkWinner())]
            if(view.winner == view.turn):
                view.loser = view.not_turn
            else:
                view.loser = view.turn
            view.disableAll()
            await interaction.response.defer()
            view.stop()

class TicTacToe(discord.ui.View):
    def __init__(self, user1: discord.User, user2: discord.User, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.buttonStatus = ["", "", "", 
                            "", "", "",
                            "", "", ""]
        self.userAssignments = {user1: "X", user2: "O"}
        row = 1
        buttonNumber = 0
        for a in range(3):
            for b in range(3):
                self.add_item(TicTacToeButton(row, buttonNumber))
                buttonNumber += 1
            row += 1
        self.turn = user1
        self.not_turn = user2
        self.interaction = interaction
        self.winner = None
        self.loser = None
        self.tie = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.turn:
            if interaction.user == self.not_turn:
                await interaction.response.send_message(content = "It is not your turn!", ephemeral = True)
            else:
                await interaction.response.defer()
            return False
        return True

    def checkWinner(self):
        for i in range(3):
            if self.buttonStatus[i] == self.buttonStatus[3 + i] and self.buttonStatus[3 + i] == self.buttonStatus[6 + i]:
                if self.buttonStatus[i] != "":
                    self.children[i].style = discord.ButtonStyle.blurple
                    self.children[3 + i].style = discord.ButtonStyle.blurple
                    self.children[6 + i].style = discord.ButtonStyle.blurple
                    return self.buttonStatus[i]
        for i in range(3):
            if self.buttonStatus[i*3] == self.buttonStatus[1 + (i*3)] and self.buttonStatus[1 + (i*3)] == self.buttonStatus[2 + (i*3)]:
                if self.buttonStatus[i*3] != "":
                    self.children[i*3].style = discord.ButtonStyle.blurple
                    self.children[1 + i*3].style = discord.ButtonStyle.blurple
                    self.children[2 + i*3].style = discord.ButtonStyle.blurple
                    return self.buttonStatus[i*3]
        if self.buttonStatus[0] == self.buttonStatus[4] and self.buttonStatus[4] == self.buttonStatus[8]:
            if self.buttonStatus[0] != "":
                self.children[0].style = discord.ButtonStyle.blurple
                self.children[4].style = discord.ButtonStyle.blurple
                self.children[8].style = discord.ButtonStyle.blurple
                return self.buttonStatus[0]
        if self.buttonStatus[2] == self.buttonStatus[4] and self.buttonStatus[4] == self.buttonStatus[6]:
            if self.buttonStatus[2] != "":
                self.children[2].style = discord.ButtonStyle.blurple
                self.children[4].style = discord.ButtonStyle.blurple
                self.children[6].style = discord.ButtonStyle.blurple
                return self.buttonStatus[2]
        return None

    def checkTie(self):
        for char in self.buttonStatus:
            if char == "":
                return False
        return True

    def disableAll(self):
        button: TicTacToeButton
        for button in self.children:
            button.disabled = True
# End Tic Tac Toe


# Confirm Prompt
class ConfirmPrompt(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.confirmed = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        await interaction.response.defer()
        self.stop()
# End Confirm Prompt



# Hangman Game
class HangmanModal(discord.ui.Modal):
    guess_letter = discord.ui.TextInput(label="Guess Letter", placeholder="Your Guess", min_length=1, max_length=1)
    
    def __init__(self):
        super().__init__(title="Guess Letter for your Hangman Game!")
        self.guessed_letter = None
        self.timed_out = False
        self.interaction: discord.Interaction = None

    async def on_submit(self, interaction: discord.Interaction):
        if self.timed_out:
            self.guessed_letter = None
            await interaction.response.send_message("Sorry, your game has timed out. Please start a new one using `/start`", ephemeral=True)
        else:
            self.guessed_letter = self.guess_letter.value
            await interaction.response.defer()
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        print(error)
        
class Hangman(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.hint_used = False
        self.save_used = False
        self.game_quit = False
        self.guessed_letter = None
        self.modal = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True

    async def on_timeout(self):
        self.modal.timed_out = True

    @discord.ui.button(label = "Guess Letter")
    async def guess(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = HangmanModal()
        self.modal = modal
        modal.interaction = interaction
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.guessed_letter = modal.guessed_letter
        self.stop()

    @discord.ui.button(label = "Hint", style = discord.ButtonStyle.blurple)
    async def hint(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.hint_used = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label = "Save", style = discord.ButtonStyle.blurple)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.save_used = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label = "Quit", style = discord.ButtonStyle.blurple)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game_quit = True
        await interaction.response.defer()
        self.stop()
# End Hangman Game


# User Settings
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
        self.newValue = None
        self.changeAllowed = None
        self.otherValue = otherValue
        self.created_at = created_at
    async def on_submit(self, interaction: discord.Interaction):
        if datetime.datetime.utcnow().timestamp() - self.created_at >= 60:
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
        view.newValue = modal.newValue
        view.changeAllowed = modal.changeAllowed
        view.stop()

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
        else:
            await interaction.response.edit_message(view=None)
            view.quited = True
            view.disableAll()
            view.stop()
            return
        view.changeAllowed = True
        view.stop()

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

class UserSettings(discord.ui.View):
    def __init__(self, user, tttenabled: bool, currentSettings):
        super().__init__(timeout=60)
        self.user = user
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

# Help menu
class Help(discord.ui.View):
    def __init__(self, hex_number, user):
        super().__init__(timeout=60)
        self.current_page = 1
        self.hex_number = hex_number
        self.user = user
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True
    @discord.ui.button(emoji="\U000023ea", style=discord.ButtonStyle.blurple, disabled=True)
    async def doubleLeft(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        button.disabled = True
        self.children[1].disabled = True
        self.children[2].disabled = False
        self.children[3].disabled = False
        embed = discord.Embed(color=self.hex_number)        
        self.changePage(embed)
        await interaction.response.edit_message(embed=embed, view=self)    
    @discord.ui.button(emoji="\U00002b05", style=discord.ButtonStyle.blurple, disabled=True)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        if self.current_page == 1:
            button.disabled = True
            self.children[0].disabled = True
        self.children[2].disabled = False
        self.children[3].disabled = False
        embed = discord.Embed(color=self.hex_number)        
        self.changePage(embed)
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(emoji="\U000027a1", style=discord.ButtonStyle.blurple)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        if self.current_page == 6:
            button.disabled = True
            self.children[3].disabled = True
        self.children[0].disabled = False
        self.children[1].disabled = False
        embed = discord.Embed(color=self.hex_number)
        self.changePage(embed)
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(emoji="\U000023e9", style=discord.ButtonStyle.blurple)
    async def doubleRight(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 6
        button.disabled = True
        self.children[0].disabled = False
        self.children[1].disabled = False
        self.children[2].disabled = True
        embed = discord.Embed(color=self.hex_number)        
        self.changePage(embed)
        await interaction.response.edit_message(embed=embed, view=self)    
    def changePage(self, embed: discord.Embed):
        if self.current_page == 1:
            embed.title = "Page 1 - How to play hangman using Aadit's Hangman"
            embed.description = "How can you play hangman using what we have created?"
            embed.add_field(name="Using the bot (me)!", value="Simply use the </start:1033466791495745577> command after creating an account using </create-account:1033637464356687943>! Invite link: https://dsc.gg/hangman")
            embed.add_field(name="Using the web app!", value="Visit https://aadits-hangman.herokuapp.com and log in with discord (You don't have to, but then you just won't earn coins)!")
            embed.add_field(name="Install Python Package!", value="Install the python package from https://pypi.org/project/AaditsHangman/ ! (You will not earn coins)")
            embed.add_field(name="Support Server", value = "https://discord.gg/CRGE5nF")
        elif self.current_page == 2:
            embed.title = "Page 2 - Accounts and Privacy"
            embed.description = "Some random things that you need to agree to and stuff"
            embed.add_field(name="</policy:1033637464356687945>", value="The privacy policy and terms of service of the bot!")
            embed.add_field(name="</create-account:1033637464356687943>", value="Create an account with the bot so that you can use its commands!")
            embed.add_field(name="</delete-account:1033637464356687944>", value="Opt out of the privacy policy by deleting your account with the bot. Hopefully you never use this command :wink:")
        elif self.current_page == 3:
            embed.title = "Page 3 - Game Commands"
            embed.description = "What can you play?"
            embed.description = "Playing games with the bot (requires for you to have an account)!"
            embed.add_field(name="</start:1033466791495745577>", value="Start a hangman game with the bot! If you win, you earn 7 coins!")
            embed.add_field(name="/tictactoe", value="Bet a certain amount of coins against another user in a game of tic tac toe! (This can be disabled if you want - see next page)")
        elif self.current_page == 4:
            embed.title = "Page 4 - Config Settings"
            embed.description = "Do you have a bunch of poor people who keep betting like 2 coins against you? Why don't you configure your setting for minimum tic tac toe bet? (use the command below)"
            embed.add_field(name="/settings", value="Change your user settings using a dropdown! This can help if you do not want pings for tic tac toe games, if you want a better interface for hangman games, ect.")
        elif self.current_page == 5:
            embed.title = "Page 5 - Using Coins"
            embed.description = "So you just earned so many coins... What can you do with them?"
            embed.add_field(name="</bal:1033466791495745580>", value="Check how many coins and other stuff you have")
            embed.add_field(name="</shop:1033466791495745584>", value="See what you can buy from the shop!")
            embed.add_field(name="</buy:1033466791495745583>", value="Buy something from the shop!")
            embed.add_field(name="</pay:1033466791529291818>", value="Give one of your poor friends some coins!")
        elif self.current_page == 6:
            embed.title = "Page 6 - Miscellaneous"
            embed.description = "Other commands that don't fall in any category"
            embed.add_field(name="</rich:1033466791529291819>", value="See the richest ~~sweats~~ users in the bot! If you want to see your name on the leaderboard, then you need to grind a lot! But if you do, you get to flex on your friends!")
            embed.add_field(name="</servers:1033466791495745586>", value="See the server count of the bot!")
            embed.add_field(name="</ping:1033466791495745579>", value="See the response time of the bot!")
            embed.add_field(name="</invite:1037581414016757851>", value="Invite the bot to your own server!")
            embed.add_field(name="</vote:1033466791495745585>", value="Earn saves by voting for the bot on various bot lists!")
            embed.add_field(name="</help:1033466791495745578>", value="This")
    