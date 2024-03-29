import discord

# View for /tictactoe command

# Implementation each of the 9 buttons in the tic tac toe game
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

# View which contains the 9 buttons, each of them implemented in TicTacToeButton
class TicTacToe(discord.ui.View):
    def __init__(self, user1: discord.User, user2: discord.User, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.buttonStatus = ["", "", "", 
                            "", "", "",
                            "", "", ""]
        # States which user is X and which user is O
        self.userAssignments = {user1: "X", user2: "O"}
        row = 1
        buttonNumber = 0
        # Adding 9 TicTacToeButtons to this view, with 3 in each row
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
        # Checks if all of the values in self.buttonStatus contain either "X" or "O"
        for char in self.buttonStatus:
            if char == "":
                return False
        return True

    def disableAll(self):
        button: TicTacToeButton
        for button in self.children:
            button.disabled = True