import discord

# Used for when the "Hangman Buttons" setting is enabled

# The modal in which the user can input a letter
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

# View which contains the 4 buttons for the hangman game where one of them triggers a modal implemented in HangmanModal
class Hangman(discord.ui.View):
    def __init__(self, user: discord.User):
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