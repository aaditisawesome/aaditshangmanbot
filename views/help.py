import discord

# Buttons for the help command and editing the embed based on the current page number
class Help(discord.ui.View):
    def __init__(self, hex_number, user):
        super().__init__(timeout=None)
        self.current_page = 1
        self.hex_number = hex_number
        self.user = user
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True

    # Children list order:
    # [Double left button, left button, right button, Double right button]
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
            embed.title = "Page 1 - Getting Started"
            embed.description = "Welcome to Aadit's Hangman Bot! Here's how to get started."
            embed.add_field(name="</create-account:1033637464356687943>", value="Create an account to start playing games and earning coins!")
            embed.add_field(name="/hangman", value="Start a game of hangman after creating your account!")
            embed.add_field(name="/help", value="View this help menu to learn about all commands")
            embed.add_field(name="Support Server", value="https://discord.gg/CRGE5nF")
        elif self.current_page == 2:
            embed.title = "Page 2 - Game Commands"
            embed.description = "All the games you can play to earn coins!"
            embed.add_field(name="/hangman (singleplayer | multiplayer)", value="Play hangman! Singleplayer wins earn 7 coins. Multiplayer can be disabled in settings.")
            embed.add_field(name="/hangman tournament", value="Start a tournament with up to 20 players!")
            embed.add_field(name="/minesweeper", value="Play minesweeper! Wins earn 15 coins.")
            embed.add_field(name="/tictactoe", value="Bet coins against other users in tic-tac-toe!")
            embed.add_field(name="/categories", value="View all available word categories and their rewards")
        elif self.current_page == 3:
            embed.title = "Page 3 - Currency Commands"
            embed.description = "Commands for managing your coins and items"
            embed.add_field(name="/balance", value="Check your coin balance and items")
            embed.add_field(name="/shop", value="View items you can buy with coins")
            embed.add_field(name="/buy", value="Purchase items from the shop")
            embed.add_field(name="/pay", value="Send coins to other users")
            embed.add_field(name="/boost-status", value="Check remaining time on your coin boost")
        elif self.current_page == 4:
            embed.title = "Page 4 - Settings & Info"
            embed.description = "Configure your settings and view information"
            embed.add_field(name="/settings", value="Configure your user settings (multiplayer, interface, etc.)")
            embed.add_field(name="/level", value="Check your current level and XP")
            embed.add_field(name="/leaderboard", value="View top players and their stats")
            embed.add_field(name="/ping", value="Check the bot's response time")
        elif self.current_page == 5:
            embed.title = "Page 5 - Support & Voting"
            embed.description = "Support the bot and get rewards!"
            embed.add_field(name="/vote", value="Vote for the bot to earn saves and XP")
            embed.add_field(name="/policy", value="View the bot's privacy policy and terms of service")
            embed.add_field(name="/delete-account", value="Delete your account and data")
            embed.add_field(name="/invite", value="Get the bot's invite link")
        elif self.current_page == 6:
            embed.title = "Page 6 - Additional Info"
            embed.description = "Other useful information"
            embed.add_field(name="Bot Invite", value="https://dsc.gg/hangman")
            embed.add_field(name="Python Package", value="Install our package: https://pypi.org/project/AaditsHangman/")
            embed.add_field(name="Support Server", value="https://discord.gg/CRGE5nF")
            embed.set_footer(text="Thank you for using Aadit's Hangman Bot!")