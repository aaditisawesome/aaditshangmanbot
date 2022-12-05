import discord

# Buttons for the help command and editing the embed based on the current page number
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

    # Children list order:
    # [Double left button, left button, right button, Double right button]
    @discord.ui.button(emoji="\U000023ea", style=discord.ButtonStyle.blurple, disabled=True)
    async def doubleLeft(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        button.disabled = True
        self.children[1].disabled = True # 
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