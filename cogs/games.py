import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from db_actions import *
import time

from views.hangman import *
from views.tictactoe import *
from views.confirmprompt import *

# Commands which allow users to play games in the bot
class GamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        print("Games commands loaded!")

    @app_commands.command(description = "Starts a hangman game!")
    async def start(self, interaction: discord.Interaction):
        if interaction.user in self.bot.authors:
            if interaction.channel in self.bot.authors[interaction.user]:
                await interaction.response.send_message("You already have a running hangman game in this channel! Type `quit` to end it.", ephemeral=True)
                return

        await interaction.response.send_message("Starting hangman game... type \"quit\" anytime to quit.")

        hasAccount = userHasAccount(interaction.user.id)
        if not hasAccount:
            await interaction.edit_original_response(content = "You don't have an account yet! In order to play hangman, you need to create an account using `/create-account`")
            return

        if interaction.user not in self.bot.authors:
            self.bot.authors[interaction.user] = [interaction.channel]
        else:
            self.bot.authors[interaction.user].append(interaction.channel)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel


        cl = ""
        wl = ""
        tries = 9
        pic = "hangman-0.png"
        word = self.bot.rw.random_word()
        userSettings = getSettings(interaction.user.id)
        usingView = userSettings["hangman_buttons"]
        embed = discord.Embed(title = interaction.user.name + "'s hangman game")
        print(word)

        embed.add_field(name = "GAME MECHANICS:", value = "Guess letters\n- Enter \"hint\" to reveal a letter\n- Enter \"save\" to get an extra try\n- Enter \"quit\" to quit the game\n- The game times out if you don't send anything for 1 minute")
        embed.add_field(name = "Wrong Letters:", value = "None", inline = False)
        value = ""
        for i in range(len(word)):
            value = value +  "\_  "
        embed.add_field(name = "Word:", value = value, inline = False)
        embed.add_field(name = "Wrong Tries Left:", value = tries)

        file = discord.File("hangman-pics/" + pic, filename=pic)
        embed.set_image(url=f"attachment://{pic}")
        embed.set_footer(text = "Please enter your next guess. (or \"hint\"/\"save\"/\"quit\")")

        if not usingView:
            await interaction.edit_original_response(content = "", attachments = [file], embed=embed)
        else:
            view = Hangman(interaction.user)
            await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
        embed.clear_fields()

        while True:
            try:
                if not usingView:
                    try:
                        guess = await self.bot.wait_for("message", timeout = 60.0, check=check)
                    except asyncio.TimeoutError:
                        await interaction.edit_original_response(content = "The game has timed out. Please start a new game with `/start` .", attachments = [], embed = None)
                        break
                    try:
                        await guess.delete()
                    except discord.Forbidden:
                        pass
                    str_guess = str(guess.content.lower())
                    print(guess)
                    print(str_guess)
                else:
                    await view.wait()
                    if view.guessed_letter is not None:
                        str_guess = view.guessed_letter.lower()
                    elif view.hint_used:
                        str_guess = "hint"
                    elif view.save_used:
                        str_guess = "save"
                    elif view.game_quit:
                        str_guess = "quit"
                    else:
                        await interaction.edit_original_response(content = "The game has timed out. Please start a new game with `/start` .", attachments = [], embed = None, view=None)
                        break

                if str_guess == "quit":
                    await interaction.edit_original_response(content = ("Thanks for playing! You have quit the game."), attachments = [], embed = None, view = None)
                    break
                elif str_guess == "hint":
                    await interaction.edit_original_response(content = ("Please give me a moment"), attachments = [], embed = None)
                    try:
                        changeWorked = changeItem(interaction.user.id, "hints", -1)
                        if not changeWorked:
                            embed.clear_fields()
                            embed.add_field(name = "Hint unsuccessful", value = "You don't have any hints! They cost 5 coins each! You can buy hints using `/buy hint [amount]`!")
                        else:
                            for letter in word:
                                if letter not in cl:
                                    cl = cl + letter
                                    break
                                letter = letter
                            embed.clear_fields()
                            embed.add_field(name = "Hint Used", value = "👌 One hint has been consumed, and a letter has been revealed for you!")
                    except Exception as e:
                        print(e)
                elif str_guess == "save":
                    await interaction.edit_original_response(content = ("Please give me a moment"), attachments = [], embed = None)
                    changeWorked = changeItem(interaction.user.id, "saves", -1)
                    if not changeWorked:
                        embed.clear_fields()
                        embed.add_field(name = "Save Unsuccessful", value = "You don\'t have any saves! You earn saves by voting for our bot with `/vote`, or winning giveaways in https://discord.gg/CRGE5nF !")
                    else:
                        tries += 1
                        pic = "hangman-" + str(9 - tries) + ".png"
                        embed.clear_fields()
                        embed.add_field(name = "Save Used", value = "👌 You now have an extra try!")
                elif len(str_guess) != 1:
                    embed.clear_fields()
                    embed.add_field(name = "Guess Unsuccessful", value = "You can only guess one letter at a time!")
                elif str_guess in cl or str_guess in wl:
                    embed.clear_fields()
                    embed.add_field(name = "Guess Unsuccessful", value = "You have already guessed this letter!")
                elif str_guess in word: # Guess is correct
                    cl += str_guess
                    embed.clear_fields()
                    embed.add_field(name = "✅ Guess Correct!", value = str_guess + " is in the word!")
                else: # Guess is wrong                
                    tries -= 1
                    wl += str_guess + " "
                    pic = "hangman-" + str(9 - tries) + ".png"
                    embed.clear_fields()
                    embed.add_field(name = "🔴 Guess Wrong", value = str_guess + " is not in the word :( !")
                    print(word)
                
                # Outputting wrong and correct letters
                cl_txt = ""
                for letter in word:
                    if letter in cl:
                        cl_txt += letter + " "
                    else:
                        cl_txt += "\_  "
                if "_" not in cl_txt:
                    embed.clear_fields()
                    embed.title = ":tada: " + interaction.user.name + " won the hangman game! :tada:"
                    userSettings = getSettings(interaction.user.id)
                    if(time.time() - userSettings["boost"] <= 3600):
                        embed.add_field(name = ":tada: You Won! :tada:", value = "You got 14 coins, good job!")
                    else:
                        embed.add_field(name = ":tada: You Won! :tada:", value = "You got 7 coins, good job!")
                    embed.set_footer(text = "Thanks for playing!")
                    if not interaction.app_permissions.manage_messages:
                        embed.set_footer(text="If you give me the \"Manage Messages\" permission, I will be able to delete the messages so you don't need to keep scrolling up!")
                elif tries == 0:
                    embed.clear_fields()
                    embed.title = "👎 " + interaction.user.name + " lost the hangman game! 👎"
                    embed.add_field(name = "🔴 You Lost!", value = "The word was ||" + word + "||")
                    embed.set_footer(text = "Please try again!")
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
                if usingView:
                    if "_" not in cl_txt or tries == 0:
                        await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=None)
                    else:
                        view = Hangman(interaction.user)
                        await interaction.edit_original_response(content = "", attachments = [file], embed=embed, view=view)
                else:
                    await interaction.edit_original_response(content = "", attachments = [file], embed=embed)
                if "_" not in cl_txt:
                    if(time.time() - userSettings["boost"] <= 3600):
                        changeItem(interaction.user.id, "coins", 14)
                    else:
                        changeItem(interaction.user.id, "coins", 7)
                    break
                elif tries == 0:
                    break
            except Exception as e:
                await interaction.edit_original_response(content = ("OOF! There was an error... DM <@697628625150803989> with this error: `" + str(e) + "`"), attachments = [], embed = None, view=None)
                if len(self.bot.authors[interaction.user]) > 1:
                    self.bot.authors[interaction.user].remove(interaction.channel)
                else:
                    self.bot.authors.pop(interaction.user)
                raise e
        if len(self.bot.authors[interaction.user]) > 1:
            self.bot.authors[interaction.user].remove(interaction.channel)
        else:
            self.bot.authors.pop(interaction.user)

    @app_commands.command()
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.User, bet: int):
        if bet <= 0:
            return await interaction.response.send_message("Enter a bet greater than 0!")
        if opponent.bot:
            return await interaction.response.send_message("No way you want to play with a bot lol")
        if interaction.user == opponent:
            return await interaction.response.send_message("Bruh, make some friends. You can't play with yourself!")
        if not userHasAccount(interaction.user.id):
            return await interaction.response.send_message("You don\'t have an account yet! Create one using `/create-account`!")
        if not userHasAccount(opponent.id):
            return await interaction.response.send_message("The opponent you mentioned doesn't have an account yet!")

        user1Settings = getSettings(interaction.user.id)
        user2Settings = getSettings(opponent.id)
        if not user1Settings["ticTacToe"]:
            return await interaction.response.send_message("You do not have tic tac toe enabled in your user settings! Enable it using `/settings`!")
        if not user2Settings["ticTacToe"]:
            return await interaction.response.send_message("Your opponent does not have tic tac toe enabled in their settings! (`/settings`)")
        if user1Settings["minTicTacToe"] != None and bet < user1Settings["minTicTacToe"]:
            return await interaction.response.send_message(f"You cannot bet below your minimum bet: {user1Settings['minTicTacToe']} coins. Configure this using `/settings`!")
        if user2Settings["minTicTacToe"] != None and bet < user2Settings["minTicTacToe"]:
            return await interaction.response.send_message(f"Your bet is below your opponent's minimum bet amount: {user2Settings['minTicTacToe']} coins. (`/settings`)!")
        if user1Settings["maxTicTacToe"] != None and bet > user1Settings["maxTicTacToe"]:
            return await interaction.response.send_message(f"You cannot bet above your maximum bet: {user1Settings['maxTicTacToe']} coins. Configure this using `/settings`!")
        if user2Settings["maxTicTacToe"] != None and bet > user2Settings["maxTicTacToe"]:
            return await interaction.response.send_message(f"Your bet is above your opponent's maximum bet amount: {user2Settings['maxTicTacToe']} coins. (`/settings`)!")
        
        user1Balance = int(getItems(interaction.user.id)[0])
        if user1Balance < bet:
            return await interaction.response.send_message(content="You don't have that many coins! Please enter a bet that you can afford.")
        user2Balance = int(getItems(opponent.id)[0])
        if user2Balance < bet:
            return await interaction.response.send_message(content="Your opponent doesn't have that many coins! Enter a smaller bet or a richer opponent.")

        confirmView = ConfirmPrompt(opponent)
        await interaction.response.send_message(content=opponent.mention + ", do you accept " + interaction.user.mention + "'s bet of " + str(bet) + " coins for winning a Tic Tac Toe game? (If you lose, you lose " + str(bet) + " coins!)", view=confirmView)
        await confirmView.wait()
        if confirmView.confirmed == None:
            return await interaction.edit_original_response(content="Your opponent didn't respond in time", view=None)        
        if not confirmView.confirmed:
            return await interaction.edit_original_response(content="Your opponent has denied your bet", view=None)
        view = TicTacToe(user1 = interaction.user, user2 = opponent, interaction=interaction)
        await interaction.edit_original_response(content = interaction.user.mention + " vs " + opponent.mention + ": Tic Tac Toe\n\n" + interaction.user.mention + ", it is your turn! You have 1 minute to respond before you automatically lose!", view=view)
        await view.wait()
        if view.winner is None and not view.tie:
            view.disableAll()
            changeItem(view.not_turn.id, "coins", bet)
            changeItem(view.turn.id, "coins", -1 * bet)
            return await interaction.edit_original_response(content = interaction.user.mention + " vs " + opponent.mention + ": Tic Tac Toe\n\nThe game has timed out, so " + view.not_turn.mention + " automatically won!\n" + view.not_turn.mention + " won " + str(bet) + " coins, and " + view.turn.mention + " lost " + str(bet) + " coins!", view=view)
        await interaction.edit_original_response(content = view.not_turn.mention + " won!\n" + view.winner.mention + " won " + str(bet) + " coins, and " + view.loser.mention + " lost " + str(bet) + " coins!", view=view)
        changeItem(view.winner.id, "coins", bet)
        changeItem(view.loser.id, "coins", -1 * bet)

async def setup(bot):
    await bot.add_cog(GamesCog(bot=bot))