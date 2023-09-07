import discord
import random

# Used for viewing level rewards in the /level command
class LevelRewards(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.defer()
            return False
        return True

    @discord.ui.button(label="View Rewards", style=discord.ButtonStyle.grey)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        embed = hex_number = random.randint(0,16777215)
        embed = discord.Embed(color=hex_number)
        embed.add_field(name = "Level 5", value = "10 saves")
        embed.add_field(name = "Level 10", value = "New Category: Objects")
        embed.add_field(name = "Level 15", value = "100 coins")
        embed.add_field(name = "Level 30", value = "35 hints")
        embed.add_field(name = "Level 50", value = "New Category: Animals")
        embed.add_field(name = "Level 75", value = "200 hints")
        embed.add_field(name = "Level 100", value = "New Category: Countries")
        embed.add_field(name = "Level 1000", value = "Boost (2x coins) for 30 days")
        await interaction.response.send_message(embed=embed)