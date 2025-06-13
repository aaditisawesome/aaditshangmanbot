import discord
import datetime
from db_actions import *
import random
from bot import HangmanBot

class LeaderboardDropdown(discord.ui.Select):
    def __init__(self, bot: HangmanBot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Coins", value = "coins", description=""),
            discord.SelectOption(label="Level", value = "level", description=""),
            discord.SelectOption(label="Votes", value = "votes", description="")
        ]
        super().__init__(options=options, placeholder="Coins")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        self.placeholder = self.values[0].capitalize()
        embed = await self.create_embed(self.values[0], interaction.user)
        await interaction.edit_original_response(content="", embed=embed, view=self.view)

    async def create_embed(self, type: str, user: discord.User):
        hex_number = random.randint(0, 16777215)
        richEmbed = discord.Embed(title=f"{type.capitalize()} Leaderboard", color=hex_number)

        sortedUsers = HangmanBot().db.getRich(type)  # Now a sorted list of full user entries
        msg = ""
        top5 = False
        user_rank = None
        user_coins = None

        # Show top 10
        for i, entry in enumerate(sortedUsers[:10]):
            user_id = entry['_id']
            val = entry[type]
            if val == 0:
                break
            if str(user_id) == str(user.id):
                top5 = True
            useradd = await self.bot.fetch_user(user_id)
            msg += f"{i + 1}. **{useradd.name}**: {val}\n"

        # Find user's rank if not in top 10
        if not top5:
            for i, entry in enumerate(sortedUsers):
                if str(entry['_id']) == str(user.id):
                    user_rank = i + 1
                    user_coins = entry[type]
                    break
            if user_rank is not None:
                msg += f". . .\n{user_rank}. **{user.name}**: {user_coins}"

        richEmbed.description = msg
        return richEmbed

class Leaderboard(discord.ui.View):
    def __init__(self, user: discord.User, bot: HangmanBot):
        super().__init__(timeout=None)
        self.user = user
        self.dropdown = LeaderboardDropdown(bot)
        self.add_item(self.dropdown)
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True
    async def create_original_embed(self):
        return await self.dropdown.create_embed("coins", self.user)