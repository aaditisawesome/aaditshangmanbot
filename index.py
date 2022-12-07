import discord
from discord.ext import commands, tasks
from random_words import RandomWords
import os

class HangmanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default();
        intents.message_content = True
        super().__init__(command_prefix="$", intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
        self.authors = {} # Dict containing ppl who have a hangman game running (Format: {author: discord.User, channels which have running hangman game: [discord.TextChannel]})
        self.rw = RandomWords()
        self.index = 0

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
        await self.tree.sync()

    async def on_ready(self):
        print("Online!")

HangmanBot().run(os.environ["token"])