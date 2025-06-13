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
            await interaction.response.defer()
            self.stop()

class TournamentGame(discord.ui.View):
    def __init__(self, users: list[discord.User], rounds: int, original_interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.scores = {user: 0 for user in users}
        self.word = self.get_word()
        # self.word = "a"
        self.original_interaction = original_interaction

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

        await interaction.response.send_message("Starting Hangman Game...", ephemeral=True)

        cl = ""
        wl = ""
        word = self.word
        tries = 9
        pic = "hangman-0.png"
        embed = discord.Embed(title = interaction.user.name + "'s hangman game")
        category = "All"

        embed.add_field(name = "GAME MECHANICS:", value = "Guess letters\n- Enter \"quit\" to quit the game\n")
        embed.add_field(name = "Category", value = category)
        embed.add_field(name = "Wrong Letters:", value = "None", inline = False)
        value = ""
        for i in range(len(word)):
            print(word[i] == "\n" or word[i] == " ")
            if word[i] == "\n" or word[i] == " ":
                value += "  "
            else:
                value += "\_ "
        print(value)
        embed.add_field(name = "Word:", value = value, inline = True)
        embed.add_field(name = "Wrong Tries Left:", value = tries)

        file = discord.File("hangman-pics/" + pic, filename=pic)
        embed.set_image(url=f"attachment://{pic}")
        embed.set_footer(text = "Please enter your next guess (or \"quit\").")

        view = Hangman(interaction.user, False)
        await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
        embed.clear_fields()

        while True:
            await view.wait()
            if view.guessed_letter is not None:
                guess_content = view.guessed_letter.lower()
            elif view.game_quit:
                guess_content = "quit"
            else:
                self.completed.append(interaction.user)
                self.completedmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                await interaction.edit_original_response(content = "The game has timed out, so you lost.", attachments = [], embed = None, view=None)
                break

            if guess_content == "quit":
                self.completed.append(interaction.user)
                self.completedmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                await interaction.edit_original_response(content = ("Thanks for playing! You have quit the game."), attachments = [], embed = None, view = None)
                break
            elif len(guess_content) != 1:
                embed.clear_fields()
                embed.color = discord.Colour.orange()
                embed.add_field(name = "Guess Unsuccessful", value = "You can only guess one letter at a time!")
            elif guess_content not in "abcdefghijklmnopqrstuvwxyz":
                embed.clear_fields()
                embed.color = discord.Colour.orange()
                embed.add_field(name = "Guess Unsuccessful", value = "Your guess must be in the alphabet!")
            elif guess_content in cl or guess_content in wl:
                embed.clear_fields()
                embed.color = discord.Colour.orange()
                embed.add_field(name = "Guess Unsuccessful", value = "You have already guessed this letter!")
            elif guess_content in word: # Guess is correct
                cl += guess_content
                embed.clear_fields()
                embed.color = discord.Colour.dark_green()
                embed.add_field(name = "✅ Guess Correct!", value = guess_content + " is in the word!")
            else: # Guess is wrong                
                tries -= 1
                wl += guess_content + " "
                pic = "hangman-" + str(9 - tries) + ".png"
                embed.clear_fields()
                embed.color = discord.Colour.red()
                embed.add_field(name = "🔴 Guess Wrong", value = guess_content + " is not in the word :( !")
                print(word)
            
            # Outputting wrong and correct letters
            cl_txt = ""
            for letter in word:
                if letter in cl:
                    cl_txt += letter + " "
                elif letter == "\n" or letter == " ":
                    cl_txt += "  "
                else:
                    cl_txt += "\_ "
            if "_" not in cl_txt:
                embed.clear_fields()
                embed.title = ":tada: " + interaction.user.name + " won the hangman game! :tada:"
                embed.color = discord.Colour.brand_green()
                embed.add_field(name = ":tada: You Won! :tada:", value = f"Please wait for others to finish their games.")
                embed.set_footer(text = "Thanks for playing!")
            elif tries == 0:
                embed.clear_fields()
                embed.color = discord.Colour.dark_red()
                embed.title = "👎 " + interaction.user.name + " lost the hangman game! 👎"
                embed.add_field(name = "🔴 You Lost!", value = "The word was ||" + word + "||. Please wait for others to finish their games.")
            embed.add_field(name = "Category:", value = category)
            if wl == "":
                embed.add_field(name = "Wrong Letters:", value = "None", inline = False)
            else:
                embed.add_field(name = "Wrong Letters:", value = wl, inline = False)
            print(cl_txt)
            embed.add_field(name = "Word:", value = cl_txt)
            embed.add_field(name = "Wrong tries left:", value = tries)
            if tries > 9: # If there are more than 9 tries left (due to saves)
                pic = "hangman-0.png"
            file = discord.File("hangman-pics/" + pic, filename=pic)
            embed.set_image(url = f"attachment://{pic}")
            if "_" in cl_txt and tries != 0:
                embed.set_footer(text = "Please enter your next guess. (or \"hint\"/\"save\"/\"quit\")")
            if "_" not in cl_txt or tries == 0:
                await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=None)
            else:
                view = Hangman(interaction.user, False)
                await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
            if "_" not in cl_txt:
                self.winners.append(interaction.user)
                self.completed.append(interaction.user)
                self.completedmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                print(self.notcompletedmsg)
                break
            elif tries == 0:
                self.completed.append(interaction.user)
                self.completedmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                break
        if len(self.completed) == len(self.scores.keys()):
            if(self.curround >= self.rounds):
                await self.original_interaction.edit_original_response(embed=self.create_final_embed(), view=None)
                self.stop()
            else:
                await self.inter_round()
        else:
            await self.original_interaction.edit_original_response(embed=self.create_game_embed())

    def create_game_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"Round {self.curround}", description="Hangman Tournament", color=discord.Colour.orange())
        embed.add_field(name="Completed", value=self.completedmsg, inline=False)
        embed.add_field(name="Not Completed", value=self.notcompletedmsg)
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
        