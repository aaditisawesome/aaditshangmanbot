import discord
from views.hangman import *
from bot import HangmanBot

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
        if self.currentAmt >= self.max:
            await interaction.response.send_message("Sorry, the max player limit has reached.")
        elif interaction.user.id in self.users:
            await interaction.response.defer() 
            await interaction.followup.send("You have already joined.", view=LeaveGame(self, interaction, self.max), ephemeral=True)
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
    def __init__(self, users: list[discord.User], word: str, original_interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.users = users
        # self.word = word
        self.word = "a"
        self.original_interaction = original_interaction

        self.gameswon: list[discord.User] = []
        self.gameslost: list[discord.User] = []

        self.gameswonmsg: str = ""
        self.gameslostmsg: str = ""
        self.notcompletedmsg: str = ""

        for user in self.users:
            self.notcompletedmsg += user.mention + "\n"

        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user not in self.users:
            await interaction.response.defer()
            return False
        return True
    
    def create_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Hangman Tournament")
        embed.add_field(name="Games Won", value=self.gameswonmsg)
        embed.add_field(name="Games Lost", value=self.gameslostmsg)
        embed.add_field(name="Not Completed", value=self.notcompletedmsg)
        return embed

    @discord.ui.button(label="Play")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Starting Hangman Game...", ephemeral=True)

        cl = ""
        wl = ""
        word = self.word
        tries = 9
        pic = "hangman-0.png"
        embed = discord.Embed(title = interaction.user.name + "'s hangman game")
        category = "All"

        embed.add_field(name = "GAME MECHANICS:", value = "Guess letters\n- Enter \"hint\" to reveal a letter\n- Enter \"save\" to get an extra try\n- Enter \"quit\" to quit the game\n")
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
        embed.set_footer(text = "Please enter your next guess. (or \"hint\"/\"save\"/\"quit\")")

        view = Hangman(interaction.user)
        await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
        embed.clear_fields()

        while True:
            await view.wait()
            if view.guessed_letter is not None:
                guess_content = view.guessed_letter.lower()
            elif view.hint_used:
                guess_content = "hint"
            elif view.save_used:
                guess_content = "save"
            elif view.game_quit:
                guess_content = "quit"
            else:
                await interaction.edit_original_response(content = "The game has timed out. Please start a new game with `/hangman` .", attachments = [], embed = None, view=None)
                break

            if guess_content == "quit":
                await interaction.edit_original_response(content = ("Thanks for playing! You have quit the game."), attachments = [], embed = None, view = None)
                break
            elif guess_content == "hint":
                await interaction.edit_original_response(content = ("Please give me a moment"), attachments = [], embed = None)
                try:
                    changeWorked = HangmanBot().db.changeItem(interaction.user.id, "hints", -1)
                    if not changeWorked:
                        embed.clear_fields()
                        embed.color = discord.Colour.red()
                        embed.add_field(name = "Hint unsuccessful", value = "You don't have any hints! They cost 5 coins each! You can buy hints using `/buy hint [amount]`!")
                    else:
                        for letter in word:
                            if letter not in cl:
                                cl = cl + letter
                                break
                            letter = letter
                        embed.clear_fields()
                        embed.color = discord.Colour.yellow()
                        embed.add_field(name = "Hint Used", value = "👌 One hint has been consumed, and a letter has been revealed for you!")
                except Exception as e:
                    print(e)
            elif guess_content == "save":
                await interaction.edit_original_response(content = ("Please give me a moment"), attachments = [], embed = None)
                changeWorked = HangmanBot().db.changeItem(interaction.user.id, "saves", -1)
                if not changeWorked:
                    embed.clear_fields()
                    embed.color = discord.Colour.red()
                    embed.add_field(name = "Save Unsuccessful", value = "You don\'t have any saves! You earn saves by voting for our bot with `/vote`, or winning giveaways in https://discord.gg/CRGE5nF !")
                else:
                    tries += 1
                    pic = "hangman-" + str(9 - tries) + ".png"
                    embed.clear_fields()
                    embed.color = discord.Colour.yellow()
                    embed.add_field(name = "Save Used", value = "👌 You now have an extra try!")
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
                view = Hangman(interaction.user)
                await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
            if "_" not in cl_txt:
                self.gameswon.append(interaction.user)
                self.gameswonmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                print(self.notcompletedmsg)
                break
            elif tries == 0:
                self.gameslost.append(interaction.user)
                self.gameslostmsg += interaction.user.mention + "\n"
                self.notcompletedmsg = self.notcompletedmsg.replace(interaction.user.mention, "")
                break
        await self.original_interaction.edit_original_response(embed=self.create_embed())
        if len(self.gameswon) + len(self.gameslost) == len(self.users):
            self.stop()