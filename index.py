import discord
from discord import app_commands
from discord.app_commands import CommandTree
from discord.ext import commands, tasks
from random_words import RandomWords
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from PyDictionary import PyDictionary
import requests
import os
import json
from db_actions import *
import asyncio

intents = discord.Intents.default();
intents.message_content = True

"""
Config Vars
GOOGLE_CREDENTIALS: The credentials I have to log in to my Google API account to connect to gspread
token: The token of my bot
top.gg-token: My top.gg API token
discordbotlist.com-token: My discordbotlist.com API token
"""

dictionary = PyDictionary()

client = commands.Bot(command_prefix="$", intents = intents)
client.remove_command("help")
client.add_check(commands.bot_has_permissions(send_messages=True, read_messages=True).predicate)
tree = client.tree

rw = RandomWords()

authors = {}
createCmdUsed = []
deleteCmdUsed = []
index = 0

rw = RandomWords()

authors = {}
index = 0

def checkOwner(interaction):
    return interaction.user.id == 697628625150803989 or interaction.user.id == 713467569725767841 or interaction.user.id == 692195032857444412

@tasks.loop(seconds=15)
async def change_status():
    global index
    statuses = [
        "https://aadits-hangman.herokuapp.com",
        f"{len(client.guilds)} server(s)",
        "/help || /start",
        "Youtube",
        "people winning hangman",
        "Audit dev me",
        "https://discord.gg/CRGE5nF",
        "https://dsc.gg/hangman",
        "for contributions on https://github.com/aaditisawesome/aaditshangmanbot"
    ]
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=statuses[index]))
    index +=1
    if index == len(statuses):
        index = 0

@client.event
async def on_ready():
    print("Online!")
    change_status.start()
    await tree.sync()

@tree.command(name = "create-account", description = "Create a hangman account to play hangman games with the bot!")
async def create_account(interaction):
    await interaction.response.send_message("Creating account...")
    hasAccount = userHasAccount(str(interaction.user.id))
    if hasAccount:
        return await interaction.edit_original_response(content = "You already have an account!")
    await interaction.edit_original_response(content = "Before creating your hangman account, please read our privacy policy and our terms of service at https://github.com/aaditisawesome/aaditshangmanbot/blob/main/README.md. If you agree to the policy and want to proceed with your account creation, use the `/confirm-create` command.")
    if interaction.user.id not in createCmdUsed:
        createCmdUsed.append(interaction.user.id)
@tree.command(name = "confirm-create", description = "Confirm creation for your hangman account!")
async def confirm_delete(interaction):
    if interaction.user.id not in createCmdUsed:
        return await interaction.response.send_message(content = "Please use the `/create-account` command before using this one")
    await interaction.response.send_message("Creating account...")
    hasAccount = userHasAccount(str(interaction.user.id))
    if hasAccount:
        await interaction.edit_original_response(content = "You already have an account!")
    else:
        initiateUser(interaction)
        await interaction.edit_original_response(content = "Your account creation has succeeded! You can now play hangman using `/start`. If you ever want to opt out of the privacy policy, delete your account using `/delete-account`.")
    createCmdUsed.remove(interaction.user.id)

@tree.command(name = "delete-account", description = "Delete your hangman account :(")
async def delete_account(interaction):
    await interaction.response.send_message("Deleting account...")
    hasAccount = userHasAccount(str(interaction.user.id))
    if not hasAccount:
        return await interaction.edit_original_response(content = "You don\'t even have an account! Create one using `/create-account`")
    await interaction.edit_original_response(content = "Are you sure you want to delete your account? If you delete your account, all of your coins and inventory will be gone, and you will not be able to play a hangman game without creating an account again! Enter `/confirm-delete` to confirm deletion.")
    if interaction.user.id not in deleteCmdUsed:
        deleteCmdUsed.append(interaction.user.id)

@tree.command(name = "confirm-delete", description = "Confirm deletion for your hangman account")
async def confirm_delete(interaction):
    if interaction.user.id not in deleteCmdUsed:
        return await interaction.response.send_message("Please run the `/delete-account` command before running this one")
    await interaction.response.send_message("Deleting your account...")
    userDeleted = deleteUser(interaction)
    if userDeleted == True:
        if interaction.user in authors:
            authors.pop(interaction.user)
        await interaction.edit_original_response(content = "Your account has been deleted :(. Please tell us why you deleted your account in https://discord.gg/CRGE5nF so that we can improve our bot!")
    else:
        await interaction.edit_original_response(content = "You don't even have an account! What do you expect me to delete? Create an account using `/create-account`.") # I want to make sure everyone knows how to create an account
    deleteCmdUsed.remove(interaction.user.id)

@tree.command(description = "The bot's privacy policy!")
async def policy(interaction):
    await interaction.response.send_message("Here is our privacy policy: https://docs.google.com/document/d/12amP0BbgaTWvn4h9b90lfpuTafW_K-x83bhB3VbZuBU/edit?usp=sharing. If you agree to the privacy policy and want to create an account, use `/create-account`.")

@tree.command(description = "Starts a hangman game!")
async def start(interaction: discord.Interaction):
    if interaction.user in authors:
        if interaction.channel in authors[interaction.user]:
            await interaction.response.send_message("You already have a running hangman game in this channel! Type `quit` to end it.")
            return
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel
    word = rw.random_word()
    cl = ""
    wl = ""
    tries = 9
    embed = discord.Embed(title = interaction.user.name + "'s hangman game")
    print(word)
    if interaction.user not in authors:
        authors[interaction.user] = [interaction.channel]
    else:
        authors[interaction.user].append(interaction.channel)
    await interaction.response.send_message("Starting hangman game... type \"quit\" anytime to quit.")
    hasAccount = userHasAccount(str(interaction.user.id))
    if not hasAccount:
        await interaction.edit_original_response(content = "You don't have an account yet! In order to play hangman, you need to create an account using `/create-account`")
        authors.pop(interaction.user)
        return
    pic = "hangman-0.png"
    embed.add_field(name = "GAME MECHANICS:", value = "Guess letters\n- Enter \"hint\" to reveal a letter\n- Enter \"save\" to get an extra try\n- Enter \"quit\" to quit the game\n- The game times out if you don't send anything for 1 minute")
    embed.add_field(name = "Wrong Letters:", value = "None", inline = False)
    value = ""
    for i in range(len(word)):
        value = value +  "\_  "
    embed.add_field(name = "Word:", value = value, inline = False)
    embed.add_field(name = "Wrong Tries Left:", value = tries)
    file = discord.File(pic, filename=pic)
    embed.set_image(url=f"attachment://{pic}")
    embed.set_footer(text = "Please enter your next guess. (or \"hint\"/\"save\"/\"quit\")")
    await interaction.edit_original_response(content = "", attachments = [file], embed=embed)
    embed.clear_fields()
    while True:
        try:
            try:
                guess = await client.wait_for("message", timeout = 60.0, check=check)
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
            if str_guess == "quit":
                await interaction.edit_original_response(content = ("Thanks for playing! You have quit the game."), attachments = [], embed = None)
                break
            elif str_guess == "hint":
                await interaction.edit_original_response(content = ("Please give me a moment"), attachments = [], embed = None)
                try:
                    changeWorked = changeItem(interaction.user, "hints", -1)
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
                changeWorked = changeItem(interaction.user, "saves", -1)
                if not changeWorked:
                    embed.clear_fields()
                    embed.add_field(name = "Save Unsuccessful", value = "You don\'t have any saves! You earn saves by voting for our bot with `/vote`, or winning giveaways in https://discord.gg/CRGE5nF !")
                else:
                    tries += 1
                    pic = "hangman-" + str(9 - tries) + ".png"
                    if pic == "hangman--1.png":
                        pic = "hangman-0.png"
                    embed.clear_fields()
                    embed.add_field(name = "Save Used", value = "👌 You now have an extra try!")
            elif str_guess == "defenition" or str_guess == "def":
                """
                await interaction.edit_original_response(content = ('Please give me a moment')
                if creds.access_token_expired:
                    gs_client.login()
                sheet = gs_client.open('Hangman bot').sheet1
                try:
                    cell = sheet.find(str(interaction.user.id))
                    column = cell.col + 2
                    print(column)
                    print(cell.col)
                    hints = sheet.cell(cell.row, column).value
                    hints = str(hints)
                    hints = int(hints)
                    if hints == 0:
                        await interaction.edit_original_response(content = ('You don\'t have any defenitions! They cost 7 coins each! When the game is over, you can buy hints by typing `/buy defenition`!')
                    else:
                        defenition = 'Here are the defenitions of the word:\n'
                        for pos in dictionary.meaning(word):
                            defenition += f'{pos}:\n'
                            x = 0
                            for meaning in dictionary.meaning(word)[pos]:
                                x+=1
                                defenition += f'{str(x)}. {meaning}\n'
                        await interaction.edit_original_response(content = (defenition)
                except:
                    await interaction.edit_original_response(content = ('You don\'t have any defenitions! They cost 7 coins each! When the game is over, you can buy hints by typing `/buy defenition`!')
                """
            elif len(str_guess) != 1:
                embed.clear_fields()
                embed.add_field(name = "Guess Unsuccessful", value = "You can only guess one letter at a time!")
            elif str_guess in cl or str_guess in wl:
                embed.clear_fields()
                embed.add_field(name = "Guess Unsuccessful", value = "You have already guessed this letter!")
            elif str_guess in word:
                cl += str_guess
                embed.clear_fields()
                embed.add_field(name = "✅ Guess Correct!", value = str_guess + " is in the word!")
            else:                
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
            file = discord.File(pic, filename=pic)
            embed.set_image(url = f"attachment://{pic}")
            if "_" in cl_txt and tries != 0:
                embed.set_footer(text = "Please enter your next guess. (or \"hint\"/\"save\"/\"quit\")")
            await interaction.edit_original_response(content = "", attachments = [file], embed=embed)
            if "_" not in cl_txt:
                changeItem(interaction.user, "coins", 7)
                break
            elif tries == 0:
                break
        except Exception as e:
            await interaction.edit_original_response(content = ("OOF! There was an error... DM <@697628625150803989> with this error: `" + str(e) + "`"), attachments = [], embed = None)
            if len(authors[interaction.user]) > 1:
                authors[interaction.user].remove(interaction.channel)
            else:
                authors.pop(interaction.user)
            raise e
    if len(authors[interaction.user]) > 1:
        authors[interaction.user].remove(interaction.channel)
    else:
        authors.pop(interaction.user)

@tree.command(description = "Brief overview of the commands and other information")
async def help(interaction):
    hex_number = random.randint(0,16777215)
    helpEmbed = discord.Embed(title="Help", color=hex_number)
    helpEmbed.add_field(name="Commands", value="`/create-account` - Create an account in the bot so that you can play hangman! \n `/policy` - View our privacy policy \n `/delete-account` - Opt out of the privacy policy and delete your account :( \n `/start` - Start AWESOME hangman game ! \n `/bal <member>` - Check how much coins you or another member has! \n `/shop` - Check out what you can buy with your coins!\n `/buy <item> <amount(Optional)>` - buy an item from the `/shop`! If you dont add an amount, it defaults to 1.\n `/servers` - See how many servers the bot is in!\n `/pay <@user> <amount of coins>` - Pay someone some coins!\n `/ping`, `/help` - It\'s kinds obvious what these are...")
    helpEmbed.add_field(name="Playing Aadit's Hangman", value="- The hangman web app I am developing: https://aadits-hangman.herokuapp.com. \n- Installing my python package from PyPI: https://pypi.org/project/AaditsHangman/. \n- Inviting me to your server: https://dsc.gg/hangman/, and creating an account using `/create-account`.")
    helpEmbed.add_field(name="Improving Aadit's Hangman", value="You can improve our game by contacting me (https://aadits-hangman.herokuapp.com/contact) or by giving us anonymous feedback at https://aadits-hangman.herokuapp.com/feedback")
    helpEmbed.add_field(name="Still confused?", value="Join our [Support Server](https://discord.gg/CRGE5nF) or watch our [video!](https://youtu.be/8DFSjOVh1QA)")
    helpEmbed.add_field(name="Enjoying the bot?", value="If you want to add Aadit's Hangman Bot to your own server so your members can play hangman, click [HERE!](https://discord.com/oauth2/authorize?client_id=748670819156099073&scope=bot&permissions=3072) Also, please see (`/vote`) if you want to get good prizes!")
    helpEmbed.timestamp = datetime.datetime.now()
    helpEmbed.set_footer(text="Thank you so much!")
    await interaction.response.send_message("https://discord.gg/CRGE5nF", embed=helpEmbed)
@tree.command(description = "The ping of the bot")
async def ping(interaction):
    await interaction.response.send_message("Pong! `" + str(client.latency * 1000) + "ms`")
@tree.command(description = "Check how many coins you have!")
async def bal(interaction, member: discord.Member = None):
    await interaction.response.send_message("Counting money...")
    if member != None:
        items = getItems(member)
        if(len(items) > 0):
            await interaction.edit_original_response(content = (member.mention + " has " + items[0] + " coins! \n They also have " + items[1] + " hints and " + items[2] + " saves!"))
        else:
            await interaction.edit_original_response(content = "The specified user doesn't have an account! Tell them to create one using `/create-account`.")
    else:
        items = getItems(interaction.user)
        if(len(items) > 0):
            await interaction.edit_original_response(content = (interaction.user.mention + ", you have " + items[0] + " coins! \n You also have " + items[1] + " hints and " + items[2] + " saves!"))
        else:
            await interaction.edit_original_response(content = "You don't have an account yet! Create one using `/create-account`!")
@client.command(name="add-coins", description = "Owner only command")
async def add_coins(interaction, member: discord.Member, amount: int):
    if interaction.author.id != 697628625150803989 and interaction.author.id != 713467569725767841 and interaction.author.id != 692195032857444412:
        return await interaction.response.send_message("You must own the bot to use this command!")
    changeWorked = changeItem(member, "coins", amount)
    if not changeWorked:
        await interaction.response.send_message("They have no account!")
    await interaction.response.send_message("Success!")
@client.command(name = "remove-coins", description = "Owner only command")
async def remove_coins(interaction, member: discord.Member, amount: int):
    if interaction.author.id != 697628625150803989 and interaction.author.id != 713467569725767841 and interaction.author.id != 692195032857444412:
        return await interaction.response.send_message("You must own the bot to use this command!")
    transactionWorked = changeItem(member, "coins", -1 * amount)
    if not transactionWorked:
        await interaction.response.send_message("They have no account!")
    await interaction.response.send_message("Success!")
@tree.command(description = "buy an item from the shop")
async def buy(interaction, item: str, amount : int = 1):
    if item == "hint":
        await interaction.response.send_message("Giving you a hint...")
        try:
            transactionWorked = changeItem(interaction.user, "coins", -5)
            if not transactionWorked:
                await interaction.edit_original_response(content = "You don't have any coins! Get coins by typing `/start` and win!")
                return
            changeItem(interaction.user, "hints", amount)
            await interaction.edit_original_response(content = "Success! You now have " + str(amount) + " more hint(s).")
        except Exception as e:
            print(e)
    else:
        await interaction.response.send_message("That is an invalid item. Please see `/shop`")
    # Below is a new currency which has not been released yet
    """
    elif item == 'defenition' or item == 'def':
        await interaction.send('Giving you a defenition...')
        if creds.access_token_expired:
            gs_client.login()
        sheet = gs_client.open('Hangman bot').sheet1
        try:
            cell = sheet.find(str(interaction.user.id))
            column = cell.col + 1
            column_d = cell.col + 4
            coins = sheet.cell(cell.row, column).value
            defenitions = sheet.cell(cell.row, column_d).value
            coins = str(coins)
            coins = int(coins)
            defenitions = str(defenitions)
            defenitions = int(defenitions)
            if coins < 7:
                return await interaction.send('You don\'t have enough coins!')
            coins -= 5
            defenitions += 1
            sheet.update_cell(cell.row, column, coins)
            sheet.update_cell(cell.row, column_d, defenitions)
            await interaction.send('Success! You now have one more hint!')
        except Exception as e:
            print(e)
            await interaction.send('You don\'t have any coins! Get coins by typing `/start` and win!')
    """
@tree.command(description = "States what you can buy with your coins")
async def shop(interaction):
    hex_number = random.randint(0,16777215)
    shopEmbed = discord.Embed(title="Shop", color=hex_number)
    shopEmbed.add_field(name="Hints", value="**Cost**: 5 coins\n**How to buy:** `/buy hint`\n**How to use:** When you are in the middle of a game, type \"hint\" instead of a letter to use.\n**Effects:** Reveals one letter of the word for you!")
    shopEmbed.add_field(name="Saves", value="**Cost**: Can only be obtained by [giveaways](https://discord.gg/CRGE5nF) or by voting (see `/vote`)\n**How to use:** When you are in the middle of a game, type \"save\" instead of a letter to use.\n**Effects:** Gives you an extra try!!")
    shopEmbed.timestamp = datetime.datetime.now()
    shopEmbed.set_footer(text="More things coming soon!")
    await interaction.response.send_message(embed=shopEmbed)
@tree.command(description = "How you can support the bot by voting!")
async def vote(interaction):
    hex_number = random.randint(0,16777215)
    voteEmbed = discord.Embed(title="Vote for Aadit's Hangman Bot!", color=hex_number)
    voteEmbed.add_field(name="2 saves per vote (bot)", value="[Top.gg](https://top.gg/bot/748670819156099073)\n[Discord Boats](https://discord.boats/bot/748670819156099073)\n[DBL](https://discord.ly/aadits-audits-hangman-bot)")
    voteEmbed.add_field(name="No perks, but please vote (bot)", value="[Botrix.cc](https://botrix.cc/bots/748670819156099073)\n[RBL](https://bots.rovelstars.ga/bots/748670819156099073)")
    voteEmbed.add_field(name="No voting system", value="[discord.bots.gg](https://discord.bots.gg/bots/748670819156099073)\n[BOD](https://bots.ondiscord.xyz/bots/748670819156099073)")
    voteEmbed.add_field(name="Vote for our server!", value="[top.gg](https://top.gg/servers/748672765837705337)")
    voteEmbed.timestamp = datetime.datetime.now()
    voteEmbed.set_footer(text="Thank you so much for voting!")
    await interaction.response.send_message(embed=voteEmbed)
@tree.command(description = "The bot's server count")
async def servers(interaction):
    servers = list(client.guilds)
    await interaction.response.send_message(f"I am currently in {str(len(servers))} servers!")
@tree.command(description = "Owner only command")
@app_commands.check(checkOwner)
async def load(interaction):
    client.load_extension("topGG")
    await interaction.response.send_message("Done")
@tree.command(description = "Owner only command")
@app_commands.check(checkOwner)
async def post(interaction):
    if interaction.user.id == 697628625150803989:
        webs = ["top.gg", "discordbotlist.com"]
        data = ""
        for web in webs:
            if web == "top.gg":
                param_name = "server_count"
                auth = os.environ["top.gg-token"]
                url = "https://top.gg/api/bots/748670819156099073/stats"
            elif web == "discordbotlist.com":
                param_name = "guilds"
                auth = os.environ["discordbotlist.com-token"]
                url = "https://discordbotlist.com/api/v1/bots/748670819156099073/stats"
            body = {param_name: len(client.guilds)}
            headers = {"Authorization": auth}
            r = requests.post(url, data=body, headers=headers)
            try:
                data += f"{web}:\n```{r.json()}```\n"
            except Exception as e:
                data += f"{web}:\n```{e} (Error)```\n"
        await interaction.response.send_message(f"Posted server count! Results:\n\n{data}")
    else:
        await interaction.response.send_message("Only the owner of the bot can use this command")
@tree.command(description = "If you are rich and you're friend is poor, you can give them coins")
async def pay(interaction, member: discord.Member, amount: int):
    await interaction.response.send_message("Paying money...")
    transactionWorked = changeItem(interaction.user, "coins", -1 * amount)
    if not transactionWorked:
        await interaction.edit_original_response(content = "You either don't have that many coins, or you don't have an account. Create an account using `/create-account.`")
        return
    transactionWorked = changeItem(member, "coins", amount)
    if not transactionWorked:
        await interaction.edit_original_response(content = "The specified user does not have an account yet. Tell them to create one using `/createaccount`.!")
        changeItem(interaction.user, "coins", amount)
        return   
    await interaction.edit_original_response(content = f"Successfully gave {member.mention} {amount} coins!")
@tree.command(description = "See the richest people in the bot!")
async def rich(interaction):
    hex_number = random.randint(0,16777215)
    richEmbed = discord.Embed(title="Rich", color=hex_number)
    await interaction.response.send_message("Getting richest users...")
    richUsers = getRich()
    for user_id in richUsers: 
            useradd = await client.fetch_user(user_id)
            leader = "%d: %s" % (list(richUsers.keys()).index(str(user_id)) + 1, useradd.name)
            embedtext = "%s coins" % (richUsers[user_id])
            richEmbed.add_field(name=leader, value=embedtext)
    richEmbed.set_footer(text="Credit for this command goes to CodeMyGame#0923")
    await interaction.edit_original_response(content = "", embed=richEmbed)  
@tree.command(description = "Invite link for the bot!")
async def invite(interaction):
    await interaction.response.send_message("Enjoying the bot? Invite me to your own server: https://dsc.gg/hangman !")
        
client.run(os.environ["token"])