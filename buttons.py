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
        super().__init__(timeout=10)
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