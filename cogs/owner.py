import discord
from discord.ext import commands
from db_actions import *
import requests

# Owner only Commands
class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print("Owner commands loaded!")

    # This is a check
    def checkOwner(ctx):
        return ctx.author.id == 697628625150803989 or ctx.author.id == 713467569725767841

    @commands.command(name="add-coins", description = "Owner only command")
    @commands.check(checkOwner)
    async def add_coins(self, ctx: commands.Context, member: discord.Member, amount: int):
        changeWorked = self.bot.db.changeItem(member.id, "coins", amount)
        if not changeWorked:
            return await ctx.send("They have no account!")
        await ctx.send("Success!")

    @commands.command(name = "remove-coins", description = "Owner only command")
    @commands.check(checkOwner)
    async def remove_coins(self, ctx: commands.Context, member: discord.Member, amount: int):
        changeWorked = self.bot.db.changeItem(member.id, "coins", -1 * amount)
        if not changeWorked:
            return await ctx.send("They have no account!")
        await ctx.send("Success!")

    @commands.command(description = "Owner only command")
    @commands.check(checkOwner)
    async def post(self, ctx):
        if ctx.author.id == 697628625150803989:
            webs = ["top.gg", "discordbotlist.com"]
            data = ""
            for web in webs:
                if web == "top.gg":
                    param_name = "server_count"
                    auth = os.environ["topgg_token"]
                    url = "https://top.gg/api/bots/748670819156099073/stats"
                elif web == "discordbotlist.com":
                    param_name = "guilds"
                    auth = os.environ["discordbotlistcom_token"]
                    url = "https://discordbotlist.com/api/v1/bots/748670819156099073/stats"
                body = {param_name: len(self.bot.guilds)}
                headers = {"Authorization": auth}
                r = requests.post(url, data=body, headers=headers)
                try:
                    data += f"{web}:\n```{r.json()}```\n"
                except Exception as e:
                    data += f"{web}:\n```{e} (Error)```\n"
            await ctx.send(f"Posted server count! Results:\n\n{data}")
        else:
            await ctx.send("Only the owner of the bot can use this command")

    @commands.command()
    @commands.check(checkOwner)
    async def sync(self, ctx: discord.ext.commands.Context):
        await self.bot.tree.sync()
        await ctx.send("Successfully synced!")

async def setup(bot):
    await bot.add_cog(OwnerCog(bot=bot))