import discord
from discord.ext import commands, tasks
from db_actions import MongoDB
import random
from random_words import RandomWords
import os

class HangmanBot(commands.Bot):
    """
    Represents an instance of the hangman bot

    Extends discord.ext.commands.Bot
    """
    def __init__(self):
        # specify intents, and create bot
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="$", intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
        """
        A dictionary of people who a
        """
        self.authors = {} # Dict containing ppl who have a hangman game running (Format: {author: discord.User, channels which have running hangman game: [discord.TextChannel]})
        self.rw = RandomWords()
        self.blacklisted: str = os.environ["blacklisted"]
        self.index = 0
        self.tips = [
            "TIP: We now have a new item called \"boosts\"! Check them out in the `/shop`!",
            "TIP: Did you know that you can also play hangman by using buttons instead of typing out your guesses? Check out the \"Hangman buttons\" setting using `/settings`!",
            "TIP: If you are having trouble playing hangman games, because you need to scroll up every time you type a letter, you can ask an admin or mod to give the bot the `Manage Messages` permission, so that the bot can delete your message when you send a guess! If you don't have access to server staff, or the chat is really active, enable the \"Hangman Buttons\" setting using `/settings`!",
            "TIP: Did you know that you can bet coins against your friends with the bot by playing Tic-tac-toe? Start a Tic-tac-toe game with one of your friends using `/tictactoe`!",
            "TIP: There are a variety of settings that you can update using `/settings`!",
            "TIP: Do you want to gain some fame in the bot? If you gain enough coins, your name will show up in `/rich`!",
            "TIP: Am I annoying by sending you these tips so often? If you are, you can disable tips using `/settings`!",
            "TIP: Did you know what if you vote for the bot, you can earn saves, which are really helpful when you are about to lose a hangman game! See information about voting using `/vote`, and info about saves using `/shop`."
        ]
        self.db = MongoDB()
    @tasks.loop(seconds=60)
    async def change_status(self):
        statuses = [
            "http://aadits-hangman.tk",
            f"{len(self.guilds)} server(s)",
            "/help || /start",
            "Youtube",
            "people winning hangman",
            "Audit dev me",
            "https://discord.gg/CRGE5nF",
            "https://dsc.gg/hangman",
            "for contributions on https://github.com/aaditisawesome/aaditshangmanbot"
        ]
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=statuses[self.index]))
        self.index +=1
        if self.index == len(statuses):
            self.index = 0

    @change_status.before_loop
    async def before_change_status(self):
        await self.wait_until_ready()

    async def setup_hook(self):
        await self.load_extension("cogs.currency")
        await self.load_extension("cogs.games")
        await self.load_extension("cogs.info")
        await self.load_extension("cogs.owner")
        await self.load_extension("cogs.settings")
        await self.load_extension("cogs.accounts")
        self.change_status.start()

    async def on_ready(self):
        print("Online!")

    async def on_app_command_completion(self, interaction: discord.Interaction, command: discord.app_commands.Command):
        if str(interaction.user.id) in self.blacklisted:
            return
        sendTip = random.randint(1, 5)
        if (sendTip >= 4):
            if (not self.db.userHasAccount(interaction.user.id) or not self.db.getSettings(interaction.user.id)["tips"]): 
                return
            await interaction.followup.send(random.choice(self.tips), ephemeral = True)