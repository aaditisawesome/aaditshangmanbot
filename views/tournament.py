import discord
from views.hangman import *
from bot import HangmanBot
import linecache
import random
import time
import asyncio

class LeaveGame(discord.ui.View):
    def __init__(self, tournamentView, original_interaction: discord.Interaction, max: int):
        super().__init__(timeout=None)
        self.tournamentView: Tournament = tournamentView
        self.original_interaction = original_interaction
        self.max = max

    @discord.ui.button(label="Leave Game", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.tournamentView.users:
            self.tournamentView.users.remove(interaction.user.id)
            await interaction.response.edit_message(content="You have successfully left the game.", view=None)
            self.tournamentView.currentAmt -= 1
            self.tournamentView.children[0].label = f"Click to join ({self.tournamentView.currentAmt}/{self.max})"
            await self.original_interaction.edit_original_response(view=self.tournamentView)
        else:
            await interaction.response.edit_message(content="You have already left the game.", view=None)

class Tournament(discord.ui.View):
    def __init__(self, max: int, user: discord.User):
        super().__init__(timeout=None)
        self.max = max
        self.currentAmt = 0
        self.users: list[discord.User] = []
        self.author = user
        self.children[0].label = f"Click to join ({self.currentAmt}/{self.max})"
        self.started = False

    @discord.ui.button()
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.users:
            await interaction.response.defer() 
            await interaction.followup.send("You have already joined.", view=LeaveGame(self, interaction, self.max), ephemeral=True)
        elif self.currentAmt >= self.max:
            await interaction.response.send_message("Sorry, the max player limit has reached.", ephemeral=True)
        else:
            self.currentAmt += 1
            self.users.append(interaction.user)
            button.label = f"Click to join ({self.currentAmt}/{self.max})"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("You have successfully joined.", view=LeaveGame(self, interaction, self.max), ephemeral=True)
    
    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Only the person who started the tournament can start the game", ephemeral=True)
        else:
            if self.currentAmt < 2:
                await interaction.response.send_message("There must be at least 2 players to start the game", ephemeral=True)
                return
            self.started = True
            await interaction.response.defer()
            self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("Only the person who started the tournament can cancel the game", ephemeral=True)
        else:
            self.started = False
            await interaction.response.defer()
            self.stop()

class TournamentGame(discord.ui.View):
    def __init__(self, users: list[discord.User], rounds: int, original_interaction: discord.Interaction, play_hangman_func):
        super().__init__(timeout=None)
        self.scores = {user: 0 for user in users}
        self.word = self.get_word()
        self.original_interaction = original_interaction
        self.play_hangman = play_hangman_func

        self.completed: list[discord.User] = []
        self.winners: list[discord.User] = []

        self.rounds = rounds
        self.curround = 1

        self.completedmsg: str = ""
        self.notcompletedmsg: str = ""

        for user in users:
            self.notcompletedmsg += user.mention + "\n"
        
        # Start timeout task for each user
        self.timeout_tasks = {}
        for user in users:
            self.timeout_tasks[user] = asyncio.create_task(self.timeout_user(user))
        self.timeouted = []

    async def timeout_user(self, user: discord.User):
        await asyncio.sleep(60)  # Wait for 1 minute
        if user not in self.completed:
            self.completed.append(user)
            self.completedmsg += user.mention + "\n"
            self.notcompletedmsg = self.notcompletedmsg.replace(user.mention, "")
            self.timeouted.append(user)
            
            if len(self.completed) == len(self.scores.keys()):
                await self.inter_round()
            else:
                await self.original_interaction.edit_original_response(embed=self.create_game_embed())

    async def inter_round(self):
        if(self.curround >= self.rounds):
            await self.original_interaction.edit_original_response(embed=self.create_final_embed(), view=None)
            self.stop()
        else:
            if len(self.winners) > 0:
                self.scores[self.winners[0]] += 3
            if len(self.winners) > 1:
                self.scores[self.winners[1]] += 2
            if len(self.winners) > 2:
                self.scores[self.winners[2]] += 1

            await self.original_interaction.edit_original_response(embed=self.create_results_embed(), view=None)
                
            self.completed = []
            self.winners = []
            self.completedmsg = ""
            self.curround += 1
            self.timeouted = []
            self.word = self.get_word()
            for user in self.scores.keys():
                self.notcompletedmsg += user.mention + "\n"
            time.sleep(30)
            self.timeout_tasks = {}
            for user in self.scores.keys():
                self.timeout_tasks[user] = asyncio.create_task(self.timeout_user(user))
            await self.original_interaction.edit_original_response(embed=self.create_game_embed(), view=self)


    def get_word(self):
        file = "words/all.txt"
        def count_generator(reader):
            b = reader(1024 * 1024)
            while b:
                yield b
                b = reader(1024 * 1024)
        with open(file, 'rb') as fp:
            c_generator = count_generator(fp.raw.read)
            # count each \n
            count = sum(buffer.count(b'\n') for buffer in c_generator) + 1
        return linecache.getline(file, random.randrange(1, count + 1)).lower()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user not in self.scores.keys():
            await interaction.response.defer()
            return False
        return True

    @discord.ui.button(label="Play")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.timeouted:
            await interaction.response.send_message("You have timed out, so you lost.", ephemeral=True)
            return
        # Cancel the timeout task for this user
        if interaction.user in self.timeout_tasks:
            self.timeout_tasks[interaction.user].cancel()
            del self.timeout_tasks[interaction.user]
        elif interaction.user not in self.completed:
            await interaction.response.send_message("You have already started the game.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        # Override the stop method to handle tournament-specific logic
        original_stop = self.stop
        def custom_stop():
            if "_" not in interaction.message.embeds[0].title:
                self.winners.append(interaction.user)
            self.completed.append(interaction.user)
            self.completedmsg += interaction.user.mention + "\n"
            self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
            
            if len(self.completed) == len(self.scores.keys()):
                if self.curround >= self.rounds:
                    asyncio.create_task(self.original_interaction.edit_original_response(embed=self.create_final_embed(), view=None))
                    original_stop()
                else:
                    asyncio.create_task(self.inter_round())
            else:
                asyncio.create_task(self.original_interaction.edit_original_response(embed=self.create_game_embed()))
        self.stop = custom_stop

        # Play the game using the passed in function
        await self.play_hangman(
            interaction=interaction,
            word=self.word,
            category="All",
            tries=9,
            players=[interaction.user],
            current_turn=interaction.user,
            add_hints=False,
            using_view=True
        )

    def create_game_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"Round {self.curround}", description="Hangman Tournament", color=discord.Colour.orange())
        embed.add_field(name="Completed", value=self.completedmsg, inline=False)
        embed.add_field(name="Not Completed", value=self.notcompletedmsg)
        embed.set_footer(text=f"Round {self.curround} of {self.rounds}")
        return embed

    def create_results_embed(self):
        embed = discord.Embed(title=f"Round {self.curround} Results", color=discord.Colour.green())

        placements = ["1st Place", "2nd Place", "3rd Place"]
        result_lines = [f"{placements[i]}: {self.winners[i].mention}" for i in range(len(self.winners))]
        embed.description = '\n'.join(result_lines)

        sorted_scores = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        embed.add_field(name="Current Scores", value='\n'.join(f"{key.mention}: {value}" for key, value in sorted_scores))
        embed.add_field(name="", value=f"Next round stars <t:{int(time.time()) + 30}:R>")
        embed.set_footer(text=f"Round {self.curround} of {self.rounds}")

        return embed

    def create_final_embed(self):
        if len(self.winners) > 0:
            self.scores[self.winners[0]] += 3
        if len(self.winners) > 1:
            self.scores[self.winners[1]] += 2
        if len(self.winners) > 2:
            self.scores[self.winners[2]] += 1
        
        embed = discord.Embed(title="Final Scores", color=discord.Colour.gold())

        sorted_scores = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        medals = ["🥇", "🥈", "🥉"]
        score_lines = [f"{medals[i] if i < 3 else f'{i+1}.'} {player.mention}: {score}" for i, (player, score) in enumerate(sorted_scores)]
        embed.description = '\n'.join(score_lines)

        return embed
        