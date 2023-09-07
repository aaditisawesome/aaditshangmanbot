import discord
import random
from db_actions import *
from bot import HangmanBot

class MinesweeperButton(discord.ui.Button):
    def __init__(self, row, column):
        super().__init__(row=row, label = "‎")
        self.row = row
        self.column = column
        self.message = "Welcome to the minesweeper game! You get 15 coins if you win.\nIf you would like to flag or unflag a square which you know is a mine, you may enable flag mode using the followup message which I sent!"
        self.lost = False

    async def callback(self, interaction: discord.Interaction):
        view: Minesweeper = self.view
        if view.flag_mode == True:
            if self.emoji == None:
                self.emoji = discord.PartialEmoji.from_str("<:flag:1058556172753436682>")
                self.label = None
            else:
                self.label = "‎"
                self.emoji = None
        elif self.emoji == discord.PartialEmoji.from_str("<:flag:1058556172753436682>"):
            await interaction.response.defer()
            return
        else:
            self.reveal()
        if not self.lost:
            game_won = view.check_for_win()
            if game_won:
                self.message = "You won! Enjoy your 15 coins!!!"
                view.end_screen()
                HangmanBot().db.changeItem(interaction.user.id, "coins", 15)
                await HangmanBot().db.addXp(interaction.user.id, random.randrange(25, 34), interaction)
                await view.flag_mode_message.delete()
        if self.lost:
            await view.flag_mode_message.delete()
        await interaction.response.edit_message(content=self.message, view=self.view)

    def reveal(self):
        view: Minesweeper = self.view
        if view.mines == None:
            print("e")
            view.mines = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]
            possible_mines = [] # [[row, column], [row, column]...]
            for i in range(5):
                for j in range(5):
                    if not ((i == self.row - 1 or i == self.row or i == self.row + 1) and (j == self.column - 1 or j == self.column or j == self.column + 1)):
                        possible_mines.append([i, j])
            for i in range(8):
                chosen_mine = random.choice(possible_mines)
                view.mines[chosen_mine[0]][chosen_mine[1]] = "X"
                possible_mines.remove(chosen_mine)
            print(view.mines)
        if view.mines[self.row][self.column] == "X":
            self.emoji = discord.PartialEmoji(name = "\U0000274c")
            self.label = None
            self.disabled = True
            view.reveal_all()
            self.message = "Oh no! You hit a mine! You lose."
            self.lost = True
            self.view.stop()
            return
        else:
            total_mines = 0
            for num1 in [-1, 0, 1]:
                for num2 in [-1, 0, 1]:
                    if self.row + num1 < 5 and self.row + num1 > -1 and self.column + num2 < 5 and self.column + num2 > -1:
                        if(view.mines[self.row + num1][self.column + num2] == "X"):
                            total_mines += 1
            self.disabled = True
            if(total_mines == 0):
                self.label = "‎"
                self.emoji = None
                view.reveal_around_button(self.row, self.column)
            else:
                self.emoji = discord.PartialEmoji(name = str(total_mines) + "\U000020e3")
                self.label = None

class Minesweeper(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        row = 0
        column = 0
        for i in range (5):
            for j in range(5):
                self.add_item(MinesweeperButton(row, column))
                column += 1
            row += 1
            column = 0
        self.mines = None
        self.user = user
        self.flag_mode = False
        self.flag_mode_message: discord.WebhookMessage = None
        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return False
        return True

    def reveal_around_button(self, row, column):
        for button in self.children:
            button: MinesweeperButton
            if (button.row == row - 1 or button.row == row or button.row == row + 1) and (button.column == column - 1 or button.column == column or button.column == column + 1):
                if not button.disabled:
                    button.emoji = None
                    button.reveal()

    def reveal_all(self):
        for button in self.children:
            button: MinesweeperButton
            if not button.disabled:
                button.reveal()

    def check_for_win(self):
        total_not_disabled = 0
        for button in self.children:
            button: MinesweeperButton
            if not button.disabled:
                total_not_disabled += 1
        if total_not_disabled <= 8:
            return True
        return False

    def end_screen(self):
        flower_emojis = ["\U0001f338", "\U0001f33c", "\U0001f33b", "\U0001f337", "\U0001f33a"]
        for button in self.children:
            button: MinesweeperButton
            if not button.disabled:
                button.emoji = discord.PartialEmoji(name = random.choice(flower_emojis))
                button.disabled = True

class MinesweeperFlags(discord.ui.View):
    def __init__(self, user, main_view: Minesweeper):
        super().__init__(timeout=None)
        self.user = user
        self.main_view = main_view

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.main_view.flag_mode = True
        button.disabled = True
        self.children[1].disabled = False
        await interaction.response.edit_message(content="Flag mode is currently enabled!", view=self)

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red, disabled=True)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):            
        self.main_view.flag_mode = False
        button.disabled = True
        self.children[0].disabled = False
        await interaction.response.edit_message(content="Flag mode is disabled!", view=self)

    