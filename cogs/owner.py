import discord
from discord.ext import commands
from db_actions import *
import requests
from bot import HangmanBot
from dotenv import load_dotenv
import time
from collections import defaultdict
import datetime

# Owner only Commands
class OwnerCog(commands.Cog):
    def __init__(self, bot: HangmanBot):
        self.bot = bot
        load_dotenv()
        # Analytics tracking
        self.command_usage = defaultdict(int)
        self.user_activity = defaultdict(int)  # Changed to count interactions
        self.session_start = time.time()
        self.games_played = defaultdict(int)

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
                r = requests.post(url, json=body, headers=headers)
                try:
                    data += f"{web}:\n```{r.json()}```\n"
                except Exception as e:
                    data += f"{web}:\n```{e} (Error)```\n"
            await ctx.send(f"Posted server count! Results:\n\n{data}")
        else:
            await ctx.send("Only the owner of the bot can use this command")

    @commands.command()
    @commands.check(checkOwner)
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync()
        await ctx.send("Successfully synced!")
    
    @commands.command(name="add-xp")
    @commands.check(checkOwner)
    async def add_xp(self, ctx: commands.Context, user: discord.User, xp: int):
        await self.bot.db.addXp(user.id, xp)
        await ctx.send("Successfully added xp!")

    @commands.command(name="reset-analytics", description="Reset all analytics data")
    @commands.check(checkOwner)
    async def reset_analytics(self, ctx: commands.Context):
        self.command_usage.clear()
        self.user_activity.clear()
        self.games_played.clear()
        self.session_start = time.time()
        await ctx.send("Analytics data has been reset!")

    @commands.command(name="analytics", description="Show comprehensive bot analytics and usage statistics")
    @commands.check(checkOwner)
    async def analytics(self, ctx: commands.Context):
        embed = discord.Embed(title="🤖 Bot Analytics Dashboard", color=discord.Colour.blue())
        
        # Session Statistics
        session_duration = time.time() - self.session_start
        hours = int(session_duration // 3600)
        minutes = int((session_duration % 3600) // 60)
        
        embed.add_field(
            name="📊 Session Statistics", 
            value=f"**Uptime:** {hours}h {minutes}m\n"
                  f"**Total Servers:** {len(self.bot.guilds):,}\n"
                  f"**Commands Used:** {sum(self.command_usage.values()):,}",
            inline=False
        )

        # Command Usage Analytics
        if self.command_usage:
            top_commands = sorted(self.command_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            command_text = "\n".join([f"• `{cmd}`: {count:,}" for cmd, count in top_commands])
            embed.add_field(
                name="🎮 Top Commands Used",
                value=command_text,
                inline=False
            )

        # User Activity Analytics
        if self.user_activity:
            active_users = len(self.user_activity)
            total_interactions = sum(self.user_activity.values())
            avg_interactions = total_interactions / active_users if active_users > 0 else 0
            
            embed.add_field(
                name="👥 User Activity",
                value=f"**Active Users:** {active_users:,}\n"
                      f"**Total Interactions:** {total_interactions:,}\n"
                      f"**Avg per User:** {avg_interactions:.1f}",
                inline=False
            )

        # Game Statistics
        if self.games_played:
            total_games = sum(self.games_played.values())
            embed.add_field(
                name="🎲 Game Statistics",
                value=f"**Games Played:** {total_games:,}\n"
                      f"**Hangman:** {self.games_played.get('hangman', 0):,}\n"
                      f"**Minesweeper:** {self.games_played.get('minesweeper', 0):,}\n"
                      f"**Tic Tac Toe:** {self.games_played.get('tictactoe', 0):,}",
                inline=False
            )
            
        # Recent Activity (last 24 hours)
        recent_activity = sum(1 for count in self.user_activity.values() if count > 0)
        embed.add_field(
            name="⏰ Recent Activity (24h)",
            value=f"**Active Users:** {recent_activity:,}\n"
                  f"**Commands Used:** {sum(count for cmd, count in self.command_usage.items() if time.time() - self.session_start < 86400):,}",
            inline=False
        )

        embed.set_footer(text=f"Analytics generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        embed.timestamp = datetime.datetime.now()
        
        await ctx.send(embed=embed)

    # Helper methods to track analytics
    def track_command(self, command_name: str):
        """Track command usage"""
        self.command_usage[command_name] += 1

    def track_user_activity(self, user_id: int):
        """Track user activity - increment interaction count"""
        self.user_activity[user_id] += 1

    def track_game_played(self, game_type: str):
        """Track games played"""
        self.games_played[game_type] += 1

async def setup(bot):
    await bot.add_cog(OwnerCog(bot=bot))