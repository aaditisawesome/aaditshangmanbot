import discord
from discord import app_commands
from discord.ext import commands
from db_actions import *
from buttons import *
import random

# Commands which give general info
class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print("Info commands loaded!")

    @app_commands.command(description = "Brief overview of the commands and other information")
    async def help(self, interaction: discord.Interaction):
        hex_number = random.randint(0,16777215)
        embed = discord.Embed(color=hex_number)        
        embed.title = "Page 1 - How to play hangman using Aadit's Hangman"
        embed.description = "How can you play hangman using what we have created?"
        embed.add_field(name="Using the bot (me)!", value="Simply use the </start:1033466791495745577> command after creating an account using </create-account:1033637464356687943>! Invite link: https://dsc.gg/hangman")
        embed.add_field(name="Using the web app!", value="Visit https://aadits-hangman.herokuapp.com and log in with discord (You don't have to, but then you just won't earn coins)!")
        embed.add_field(name="Install Python Package!", value="Install the python package from https://pypi.org/project/AaditsHangman/ ! (You will not earn coins)")
        embed.add_field(name="Support Server", value = "https://discord.gg/CRGE5nF")
        view = Help(hex_number, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)
        timed_out = await view.wait()
        if timed_out:
            await interaction.edit_original_response(content="Interaction timed out...", view=None)

    @app_commands.command(description = "The ping of the bot")
    async def ping(self, interaction: discord.Interaction):
        # await interaction.response.send_message("Pong! `" + str(bot.latency * 1000) + "ms`")
        interaction_creation = interaction.created_at.replace(tzinfo=None).timestamp() * 1000
        received_time = datetime.datetime.utcnow().timestamp() * 1000
        await interaction.response.send_message(f"API Latency: `{round(self.bot.latency * 1000, 2)}ms`\nPing: `{round(received_time - interaction_creation, 2)}ms`")
        respond_time = datetime.datetime.utcnow().timestamp() * 1000
        await interaction.edit_original_response(content=f"API Latency: `{round(self.bot.latency * 1000, 2)}ms`\nPing: `{round(received_time - interaction_creation, 2)}ms`\nLatency: `{round(respond_time - interaction_creation, 2)}ms`")

    @app_commands.command(description = "States what you can buy with your coins")
    async def shop(self, interaction):
        hex_number = random.randint(0,16777215)
        shopEmbed = discord.Embed(title="Shop", color=hex_number)
        shopEmbed.add_field(name="Hints", value="**Cost**: 5 coins\n**How to buy:** `/buy hint`\n**How to use:** When you are in the middle of a game, type \"hint\" instead of a letter to use.\n**Effects:** Reveals one letter of the word for you!")
        shopEmbed.add_field(name="Saves", value="**Cost**: Can only be obtained by [giveaways](https://discord.gg/CRGE5nF) or by voting (see `/vote`)\n**How to use:** When you are in the middle of a game, type \"save\" instead of a letter to use.\n**Effects:** Gives you an extra try!!")
        shopEmbed.timestamp = datetime.datetime.now()
        shopEmbed.set_footer(text="More things coming soon!")
        await interaction.response.send_message(embed=shopEmbed)

    @app_commands.command(description = "See the richest people in the bot!")
    async def rich(self, interaction):
        hex_number = random.randint(0,16777215)
        richEmbed = discord.Embed(title="Rich", color=hex_number)
        await interaction.response.send_message("Getting richest users...")
        richUsers = getRich()
        for user_id in richUsers: 
                useradd = await self.bot.fetch_user(user_id)
                leader = "%d: %s" % (list(richUsers.keys()).index(str(user_id)) + 1, useradd.name)
                embedtext = "%s coins" % (richUsers[user_id])
                richEmbed.add_field(name=leader, value=embedtext)
        richEmbed.set_footer(text="Credit for this command goes to CodeMyGame#0923")
        await interaction.edit_original_response(content = "", embed=richEmbed)  

    @app_commands.command(description = "How you can support the bot by voting!")
    async def vote(self, interaction):
        hex_number = random.randint(0,16777215)
        voteEmbed = discord.Embed(title="Vote for Aadit's Hangman Bot!", color=hex_number)
        voteEmbed.add_field(name="2 saves per vote (bot)", value="[Top.gg](https://top.gg/bot/748670819156099073)\n[Discord Boats](https://discord.boats/bot/748670819156099073)\n[DBL](https://discord.ly/aadits-audits-hangman-bot)")
        voteEmbed.add_field(name="No perks, but please vote (bot)", value="[Botrix.cc](https://botrix.cc/bots/748670819156099073)\n[RBL](https://bots.rovelstars.ga/bots/748670819156099073)")
        voteEmbed.add_field(name="No voting system", value="[discord.bots.gg](https://discord.bots.gg/bots/748670819156099073)\n[BOD](https://bots.ondiscord.xyz/bots/748670819156099073)")
        voteEmbed.add_field(name="Vote for our server!", value="[top.gg](https://top.gg/servers/748672765837705337)")
        voteEmbed.timestamp = datetime.datetime.now()
        voteEmbed.set_footer(text="Thank you so much for voting!")
        await interaction.response.send_message(embed=voteEmbed)

    @app_commands.command(description = "The bot's server count")
    async def servers(self, interaction):
        servers = list(self.bot.guilds)
        await interaction.response.send_message(f"I am currently in {str(len(servers))} servers!")

    @app_commands.command(description = "Invite link for the bot!")
    async def invite(self, interaction):
        await interaction.response.send_message("Enjoying the bot? Invite me to your own server: https://dsc.gg/hangman !")

async def setup(bot):
    await bot.add_cog(InfoCog(bot=bot))