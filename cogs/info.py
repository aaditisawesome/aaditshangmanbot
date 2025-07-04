import discord
from discord import app_commands
from discord.ext import commands
from db_actions import *
import random
import datetime
from views.help import *
from views.levelrewards import *
from views.leaderboard import *
from bot import HangmanBot

# Commands which give general info
class InfoCog(commands.Cog):
    def __init__(self, bot: HangmanBot):
        self.bot = bot

    async def cog_load(self):
        print("Info commands loaded!")

    @app_commands.command(description = "Brief overview of the commands and other information")
    async def help(self, interaction: discord.Interaction):
        hex_number = random.randint(0,16777215)
        embed = discord.Embed(color=hex_number)        
        embed.title = "Page 1 - Getting Started"
        embed.description = "Welcome to Aadit's Hangman Bot! Here's how to get started."
        embed.add_field(name="</create-account:1033637464356687943>", value="Create an account to start playing games and earning coins!")
        embed.add_field(name="/hangman", value="Start a game of hangman after creating your account!")
        embed.add_field(name="/help", value="View this help menu to learn about all commands")
        embed.add_field(name="Support Server", value="https://discord.gg/CRGE5nF")
        view = Help(hex_number, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(description = "The ping of the bot")
    async def ping(self, interaction: discord.Interaction):
        # await interaction.response.send_message("Pong! `" + str(bot.latency * 1000) + "ms`")
        interaction_creation = interaction.created_at.replace(tzinfo=None).timestamp() * 1000
        received_time = datetime.utcnow().timestamp() * 1000
        await interaction.response.send_message(f"API Latency: `{round(self.bot.latency * 1000, 2)}ms`\nPing: `{round(received_time - interaction_creation, 2)}ms`")
        respond_time = datetime.utcnow().timestamp() * 1000
        await interaction.edit_original_response(content=f"API Latency: `{round(self.bot.latency * 1000, 2)}ms`\nPing: `{round(received_time - interaction_creation, 2)}ms`\nLatency: `{round(respond_time - interaction_creation, 2)}ms`")

    @app_commands.command(description = "States what you can buy with your coins")
    async def shop(self, interaction):
        hex_number = random.randint(0,16777215)
        shopEmbed = discord.Embed(title="Shop", color=hex_number)
        shopEmbed.add_field(name="Hints", value="**Cost**: 5 coins\n**How to buy:** `/buy hint`\n**How to use:** When you are in the middle of a game, type \"hint\" instead of a letter to use.\n**Effects:** Reveals one letter of the word for you!")
        shopEmbed.add_field(name="Boost", value="**Cost**: 15 coins\n**How to buy:** `/buy boost`\n**How to use:** Automatically used when you buy it\n**Effects:** Doubles the amount of coins you get from winning hangman games for an hour!")
        shopEmbed.add_field(name="Saves", value="**Cost**: Can only be obtained by [giveaways](https://discord.gg/CRGE5nF) or by voting (see `/vote`)\n**How to use:** When you are in the middle of a game, type \"save\" instead of a letter to use.\n**Effects:** Gives you an extra try!!")
        shopEmbed.timestamp = datetime.now()
        shopEmbed.set_footer(text="More things coming soon!")
        await interaction.response.send_message(embed=shopEmbed)

    @app_commands.command(description = "See the leaderboard for different stats!")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        view = Leaderboard(interaction.user, self.bot)
        embed = await view.create_original_embed()
        await interaction.edit_original_response(content="", embed=embed, view=view)

    @app_commands.command(description = "How you can support the bot by voting!")
    async def vote(self, interaction):
        hex_number = random.randint(0,16777215)
        voteEmbed = discord.Embed(title="Vote for Aadit's Hangman Bot!", color=hex_number)
        voteEmbed.add_field(name="2 saves + xp each vote", value="[top.gg](https://top.gg/bot/748670819156099073)\n[DBL](https://discord.ly/aadits-audits-hangman-bot)")
        voteEmbed.add_field(name="Other bot lists", value="[discord.bots.gg](https://discord.bots.gg/bots/748670819156099073)\n[BOD](https://bots.ondiscord.xyz/bots/748670819156099073)")
        voteEmbed.add_field(name="Vote for our server!", value="[top.gg](https://top.gg/servers/748672765837705337)")
        voteEmbed.timestamp = datetime.now()
        voteEmbed.set_footer(text="Thank you so much for voting!")
        await interaction.response.send_message(embed=voteEmbed)

    @app_commands.command(description = "See your current level")
    async def level(self, interaction):
        userData = self.bot.db.getLevels(interaction.user.id)
        hex_number = random.randint(0,16777215)
        if userData is not None:
            embed = discord.Embed(title=interaction.user.name + "'s level", color = hex_number, description=f"\n**Level:** {userData['level']}\n**XP:** {userData['xp']}/100")
        else:
            embed = discord.Embed(title=interaction.user.name + "'s level", color = hex_number, description=f"\n**Level:** 0\n**XP:** 0/100")
        await interaction.response.send_message(embed=embed, view=LevelRewards(interaction.user))

    @app_commands.command(description = "See all hangman categories and their rewards")
    async def categories(self, interaction: discord.Interaction):
        userSettings = self.bot.db.getSettings(interaction.user.id)
        if "categories" not in userSettings:
            unlocked_categories = ["All"]
        else:
            unlocked_categories = userSettings["categories"]
        hex_number = random.randint(0,16777215)
        embed = discord.Embed(title="Categories", color=hex_number)
        embed.add_field(name = ":green_square: All (unlocked)", value = "Most words in the English dictionary\n**Coins per win:** 7")
        if "Objects" in unlocked_categories:
            embed.add_field(name = ":green_square: Objects (unlocked)", value = "Everyday Objects\n**Coins per win:** 7", inline = False)
        else:
            embed.add_field(name = ":red_square: Objects (unlocks at level 10)", value = "Most words in the English dictionary\n**Coins per win:** 7", inline = False)
        
        if "Animals" in unlocked_categories:
            embed.add_field(name = ":green_square: Animals (unlocked)", value = "An example of one is <@439641274279264256>\n**Coins per win:** 6", inline = False)
        else:
            embed.add_field(name = ":red_square: Animals (unlocks at level 50)", value = "An example of one is <@439641274279264256>\n**Coins per win:** 6", inline = False)

        if "Countries" in unlocked_categories:
            embed.add_field(name = ":green_square: Countries (unlocked)", value = "All countries around the world!\n**Coins per win:** 4", inline = False)
        else:
            embed.add_field(name = ":red_square: Countries (unlocks at level 100)", value = "All countries around the world!\n**Coins per win:** 4", inline = False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description = "The bot's server count")
    async def servers(self, interaction):
        servers = list(self.bot.guilds)
        await interaction.response.send_message(f"I am currently in {str(len(servers))} servers!")

    @app_commands.command(description = "Invite link for the bot!")
    async def invite(self, interaction):
        await interaction.response.send_message("Enjoying the bot? Invite me to your own server: https://dsc.gg/hangman !")

async def setup(bot: HangmanBot):
    await bot.add_cog(InfoCog(bot=bot))