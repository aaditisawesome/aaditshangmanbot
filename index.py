import discord
from discord.ext import commands, tasks
from random_words import RandomWords
import os

class HangmanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default();
        intents.message_content = True
        super().__init__(command_prefix="$", intents=intents)
        self.authors = {}
        self.rw = RandomWords()
        self.index = 0

    @tasks.loop(seconds=15)
    async def change_status(self):
        statuses = [
            "https://aadits-hangman.herokuapp.com",
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

    async def setup_hook(self):
        await self.load_extension("cogs.currency")
        await self.load_extension("cogs.games")
        await self.load_extension("cogs.info")
        await self.load_extension("cogs.owner")
        await self.load_extension("cogs.settings")
        self.change_status.start()

    async def on_ready(self):
        print("Online!")

HangmanBot().run(os.environ["token"])