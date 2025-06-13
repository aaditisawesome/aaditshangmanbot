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
        await interaction.response.defer()
        view: Minesweeper = self.view
        if view.flag_mode == True:
            if self.emoji == None:
                self.emoji = discord.PartialEmoji.from_str("<:flag:1058556172753436682>")
                self.label = None
            else:
                self.label = "‎"
                self.emoji = None
        elif self.emoji == discord.PartialEmoji.from_str("<:flag:1058556172753436682>"):
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
        await interaction.message.edit(content=self.message, view=self.view)

    def reveal(self):
        view: Minesweeper = self.view
        if view.mines == None:
            view.mines = [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]
            
            # First, mark the clicked cell and its surroundings as safe
            safe_cells = []
            for i in range(max(0, self.row - 1), min(5, self.row + 2)):
                for j in range(max(0, self.column - 1), min(5, self.column + 2)):
                    safe_cells.append([i, j])
            
            # Then, find all possible mine locations (excluding safe cells)
            possible_mines = []
            for i in range(5):
                for j in range(5):
                    if [i, j] not in safe_cells:
                        possible_mines.append([i, j])
            
            # Place mines ensuring logical solvability
            mines_placed = 0
            while mines_placed < 4 and possible_mines:
                # Choose a random mine location
                chosen_mine = random.choice(possible_mines)
                possible_mines.remove(chosen_mine)
                
                # Create a temporary board with this mine added
                temp_mines = [row[:] for row in view.mines]  # Deep copy
                temp_mines[chosen_mine[0]][chosen_mine[1]] = "X"
                
                # Only add the mine if it doesn't create an unsolvable situation
                if not self.would_create_unsolvable_situation(temp_mines, [self.row, self.column]):
                    view.mines[chosen_mine[0]][chosen_mine[1]] = "X"
                    mines_placed += 1
            
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

    def would_create_unsolvable_situation(self, temp_mines, start_pos):
        from copy import deepcopy
        from itertools import product

        def in_bounds(r, c):
            return 0 <= r < 5 and 0 <= c < 5

        def get_neighbors(r, c):
            return [(r+dr, c+dc) for dr, dc in product([-1, 0, 1], repeat=2)
                    if (dr != 0 or dc != 0) and in_bounds(r+dr, c+dc)]

        def generate_number_board(mine_board):
            board = [[0 for _ in range(5)] for _ in range(5)]
            for r in range(5):
                for c in range(5):
                    if mine_board[r][c] == "X":
                        board[r][c] = "X"
                        continue
                    count = 0
                    for nr, nc in get_neighbors(r, c):
                        if mine_board[nr][nc] == "X":
                            count += 1
                    board[r][c] = count
            return board

        def is_solvable_from_start(number_board, start_r, start_c):
            if number_board[start_r][start_c] == "X":
                return False  # can't start on a mine

            revealed = [[False] * 5 for _ in range(5)]
            queue = [(start_r, start_c)]
            revealed[start_r][start_c] = True

            # Reveal 0 regions and their borders
            while queue:
                r, c = queue.pop()
                if number_board[r][c] == 0:
                    for nr, nc in get_neighbors(r, c):
                        if not revealed[nr][nc] and number_board[nr][nc] != "X":
                            revealed[nr][nc] = True
                            queue.append((nr, nc))

            # Check if all safe tiles are revealed
            for r in range(5):
                for c in range(5):
                    if number_board[r][c] != "X" and not revealed[r][c]:
                        return False
            return True

        # Create number board from mine layout
        number_board = generate_number_board(temp_mines)

        # Extract start position
        start_r, start_c = start_pos

        # Return True if board is solvable from start, False if not
        return is_solvable_from_start(number_board, start_r, start_c)

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
        if total_not_disabled <= 4:
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

    