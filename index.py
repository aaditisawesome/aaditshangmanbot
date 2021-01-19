import discord
from discord.ext import commands
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

"""
Config Vars

GOOGLE_CREDENTIALS: The credentials I have to log in to my Google API account to connect to gspread
token: The token of my bot
top.gg-token: My top.gg API token
discord.boats-token: My discord.boats API token
discordbotlist.com-token: My discordbotlist.com API token
"""
scope = 'https://spreadsheets.google.com/feeds' 
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GOOGLE_CREDENTIALS']), scope)
gs_client = gspread.authorize(creds)
dictionary = PyDictionary()

client = commands.Bot(command_prefix="$", activity=discord.Game(name="https://aadits-hangman.herokuapp.com || $help"))
client.remove_command("help")
client.add_check(commands.bot_has_permissions(send_messages=True).predicate)

rw = RandomWords()

authors = []

@client.event
async def on_ready():
    print('Online!')

@client.command()
async def start(ctx):
    if ctx.author in authors:
        return
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    word = rw.random_word()
    cl = ""
    wl = ""
    tries = 9
    print(word)
    authors.append(ctx.author)
    await ctx.send('Starting hangman game... type "quit" anytime to quit.')
    time.sleep(0.5)
    pic = 'hangman-0.png'
    while True:
        try:
            cl_txt = ""
            try:
                await guess.channel.send(ctx.author.mention + ', What is your guess?')
            except UnboundLocalError:
                await ctx.send(ctx.author.mention + ', ' + ('＿  ' * len(word)) + '\nWhat is your guess?')
            guess = await client.wait_for('message', check=check)
            str_guess = str(guess.content.lower())
            print(guess)
            print(str_guess)
            if str_guess == 'quit':
                await guess.channel.send('Thanks for playing! The game is over')
                break
            elif str_guess == 'hint':
                await ctx.send('Please give me a moment')
                if creds.access_token_expired:
                    gs_client.login()
                sheet = gs_client.open('Hangman bot').sheet1
                try:
                    cell = sheet.find(str(ctx.author.id))
                    column = cell.col + 2
                    print(column)
                    print(cell.col)
                    hints = sheet.cell(cell.row, column).value
                    hints = str(hints)
                    hints = int(hints)
                    if hints == 0:
                        await ctx.send('You don\'t have any hints! They cost 5 coins each! When the game is over, you can buy hints by typing `$buy hint`!')
                    else:
                        hints -= 1
                        sheet.update_cell(cell.row, column, hints)
                        for letter in word:
                            if letter not in cl:
                                cl = cl + letter
                                break
                            letter = letter
                        for letter in word:
                            if letter in cl:
                                cl_txt += letter + ' '
                            else:
                                cl_txt += '＿  '
                        if wl == "":
                            await guess.channel.send('👌 ' + ctx.author.mention + ', a letter has been revealed for you, and you used one hint!!\n ' + cl_txt + '\n **Wrong Letters:** None\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                        else:
                            await guess.channel.send('👌 ' + ctx.author.mention + ', a letter has been revealed for you, and you used one hint!!\n ' + cl_txt + '\n **Wrong Letters:** ' + wl + '\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                        if '＿' not in cl_txt:
                            await guess.channel.send(ctx.author.mention + ', :tada: You won! :tada: You got 7 coins, and the game is over. Please wait a moment...')
                            if creds.access_token_expired:
                                gs_client.login()
                            sheet = gs_client.open('Hangman bot').sheet1
                            try:
                                cell = sheet.find(str(ctx.author.id))
                                column = cell.col + 1
                                print(column)
                                print(cell.col)
                                coins = sheet.cell(cell.row, column).value
                                coins = str(coins)
                                coins = int(coins)
                                coins += 7
                                sheet.update_cell(cell.row, column, coins)
                            except Exception as e:
                                print(e)
                                row = [ctx.author.id, 7, 0, 0, 0]
                                index = sheet.row_count + 1
                                sheet.insert_row(row, index)
                            await guess.channel.send(ctx.author.mention + ', Thanks for playing!')
                            break
                except:
                    await ctx.send('You don\'t have any hints! They cost 5 coins each! When the game is over, you can buy hints by typing `$buy hint`!')
            elif str_guess == 'save':
                await ctx.send('Please give me a moment')
                if creds.access_token_expired:
                    gs_client.login()
                sheet = gs_client.open('Hangman bot').sheet1
                try:
                    cell = sheet.find(str(ctx.author.id))
                    column = cell.col + 3
                    print(column)
                    print(cell.col)
                    saves = sheet.cell(cell.row, column).value
                    saves = str(saves)
                    saves = int(saves)
                    if saves == 0:
                        await ctx.send('You don\'t have any saves! For now, the only way to get saves are by winning giveaways in https://discord.gg/CRGE5nF !')
                    else:
                        saves -= 1
                        sheet.update_cell(cell.row, column, saves)
                        tries += 1
                        pic = 'hangman-' + str(9 - tries) + '.png'
                        if pic == 'hangman--1.png':
                            pic = 'hangman-0.png'
                        await guess.channel.send('👌 ' + ctx.author.mention + ', you now have an extra try!', file=discord.File(pic))
                except Exception as e:
                    print(e)
                    await ctx.send('You don\'t have any saves! For now, the only way to get saves are by winning giveaways in https://discord.gg/CRGE5nF !')
            elif str_guess == 'defenition' or str_guess == 'def':
                await ctx.send('Please give me a moment')
                if creds.access_token_expired:
                    gs_client.login()
                sheet = gs_client.open('Hangman bot').sheet1
                try:
                    cell = sheet.find(str(ctx.author.id))
                    column = cell.col + 2
                    print(column)
                    print(cell.col)
                    hints = sheet.cell(cell.row, column).value
                    hints = str(hints)
                    hints = int(hints)
                    if hints == 0:
                        await ctx.send('You don\'t have any defenitions! They cost 7 coins each! When the game is over, you can buy hints by typing `$buy defenition`!')
                    else:
                        defenition = 'Here are the defenitions of the word:\n'
                        for pos in dictionary.meaning(word):
                            defenition += f'{pos}:\n'
                            x = 0
                            for meaning in dictionary.meaning(word)[pos]:
                                x+=1
                                defenition += f'{str(x)}. {meaning}\n'
                        await ctx.send(defenition)
                except:
                    await ctx.send('You don\'t have any defenitions! They cost 7 coins each! When the game is over, you can buy hints by typing `$buy defenition`!')
            elif len(str_guess) != 1:
                await guess.channel.send('You can only send one letter!')
            elif str_guess in cl or str_guess in wl:
                for letter in word:
                    if letter in cl:
                        cl_txt += letter + ' '
                    else:
                        cl_txt += '＿  '
                if wl == "":
                    await guess.channel.send(ctx.author.mention + ', You have already said this letter\n' + cl_txt + '\n **Wrong Letters:** None\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                else:
                    await guess.channel.send(ctx.author.mention + ', You have already said this letter\n' + cl_txt + '\n **Wrong Letters:** ' + wl + '\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
            elif str_guess in word:
                cl += str_guess
                for letter in word:
                    if letter in cl:
                        cl_txt += letter + ' '
                    else:
                        cl_txt += '＿  '
                if wl == "":
                    await guess.channel.send('✅ ' + ctx.author.mention + ', "' + str_guess + '" is in the word!\n ' + cl_txt + '\n **Wrong Letters:** None\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                else:
                    await guess.channel.send('✅ ' + ctx.author.mention + ', "' + str_guess + '" is in the word!\n ' + cl_txt + '\n **Wrong Letters:** ' + wl + '\nYou still have ' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                if '＿' not in cl_txt:
                    await guess.channel.send(ctx.author.mention + ', :tada: You won! :tada: You got 7 coins, and the game is over. Please wait a moment...')
                    if creds.access_token_expired:
                        gs_client.login()
                    sheet = gs_client.open('Hangman bot').sheet1
                    try:
                        cell = sheet.find(str(ctx.author.id))
                        column = cell.col + 1
                        print(column)
                        print(cell.col)
                        coins = sheet.cell(cell.row, column).value
                        coins = str(coins)
                        coins = int(coins)
                        coins += 7
                        sheet.update_cell(cell.row, column, coins)
                    except Exception as e:
                        print(e)
                        row = [ctx.author.id, 7, 0, 0, 0]
                        index = sheet.row_count + 1
                        sheet.insert_row(row, index)
                    await guess.channel.send(ctx.author.mention + ', Thanks for playing!')
                    break
            else:                
                tries -= 1
                wl += str_guess + ' '
                for letter in word:
                    if letter in cl:
                        cl_txt += letter + ' '
                    else:
                        cl_txt += '＿  '
                pic = 'hangman-' + str(9 - tries) + '.png'
                await guess.channel.send('🔴 ' + ctx.author.mention + ', "' + str_guess + '" is not in the word :( !\n ' + cl_txt + '\n **Wrong Letters:** ' + wl + '\n' + str(tries) + ' wrong tries left! Please wait for a moment...', file=discord.File(pic))
                if tries == 0:
                    await guess.channel.send(ctx.author.mention + ', You lost! The game is over. 👎')
                    await guess.channel.send('The word was ' + word + ", " + ctx.author.mention)
                    break
                print(word)
                print(str_guess)
        except Exception as e:
            await ctx.send("OOF! There was an error... Please check you internet. If you internet is completley fine, DM <@765608914284052560> with this Error: `" + str(e) + '`')
            break
    authors.remove(ctx.author)

@client.command()
async def help(ctx):
    if ctx.author in authors:
        return
    hex_number = random.randint(0,16777215)
    helpEmbed = discord.Embed(title='Help', color=hex_number)
    helpEmbed.add_field(name='Commands', value='`$start` - Start AWESOME hangman game ! \n `$bal <member>` - Check how much coins you or another member has! \n `$shop` - Check out what you can buy with your coins!\n `$buy <item>` - buy an item from the `$shop`!\n `$servers` - See how many servers the bot is in!\n `$pay <@user> <amount of coins>` - Pay someone some coins!\n `$ping`, `$help` - It\'s kinds obvious what these are...')
    helpEmbed.add_field(name='Playing Aadit\'s Hangman', value='There are three ways to play. One is on https://aadits-hangman.herokuapp.com . That is a hangman app I am developing. The second way is by cloning the repo on https://aadits-hangman.herokuapp.com/github, which will open a tkinter window. Be sure to read `README.md`! The last way is with the bot. Simply type `$start` in a channel I can access!')
    helpEmbed.add_field(name='Improving Aadit\'s hangman', value='You can improve our game by contacting me (https://aadits-hangman.herokuapp.com/contact) or by giving us anonymous feedback at https://aadits-hangman.herokuapp.com/feedback')
    helpEmbed.add_field(name='Still confused?', value='Join our [Support Server](https://discord.gg/CRGE5nF) and watch our [Video!](https://youtu.be/8DFSjOVh1QA)')
    helpEmbed.add_field(name='Enjoying the bot?', value='If you want to add Aadit\'s Hangman Bot to your own server so your members can play hangman, click [HERE!](https://discord.com/oauth2/authorize?client_id=748670819156099073&scope=bot&permissions=3072) Also, please see (`$vote`) if you want to get good prizes!')
    helpEmbed.timestamp = datetime.datetime.now()
    helpEmbed.set_footer(text='Thank you so much!')
    await ctx.send('https://discord.gg/CRGE5nF', embed=helpEmbed)
@client.command()
async def ping(ctx):
    if ctx.author in authors:
        return
    await ctx.send('Pong! `' + str(client.latency * 1000) + 'ms`')
@client.command()
async def bal(ctx):
    if ctx.author in authors:
        return
    await ctx.send('Counting money...')
    if creds.access_token_expired:
        gs_client.login()
    sheet = gs_client.open('Hangman bot').sheet1
    if len(ctx.message.mentions):
        try:
            cell_m = sheet.find(str(ctx.message.mentions[0].id))
            column = cell_m.col + 1
            column_h = cell_m.col + 2
            coins = sheet.cell(cell_m.row, column).value
            coins = str(coins)
            hints = sheet.cell(cell_m.row, column_h).value
            hints = str(hints)
            column_s = cell_m.col + 3
            print(column)
            print(cell_m.col)
            saves_m = sheet.cell(cell_m.row, column_s).value
            saves_m = str(saves_m)
            await ctx.send(ctx.message.mentions[0].mention + ' has ' + coins + ' coins! \n They also have ' + hints + ' hints and ' + saves_m + ' saves!')
        except Exception as e:
            print(str(e))
            await ctx.send(ctx.message.mentions[0].mention + ' doesn\'t have any coins, hints or saves!')
    else:
        try:
            cell = sheet.find(str(ctx.author.id))
            column = cell.col + 1
            column_h = cell.col + 2
            coins = sheet.cell(cell.row, column).value
            coins = str(coins)
            hints = sheet.cell(cell.row, column_h).value
            hints = str(hints)
            cell = sheet.find(str(ctx.author.id))
            column_s = cell.col + 3
            print(column)
            print(cell.col)
            saves = sheet.cell(cell.row, column_s).value
            saves = str(saves)
            await ctx.send(ctx.author.mention + ', You have ' + coins + ' coins! \n You also have ' + hints + ' hints and ' + saves + ' saves!')
        except Exception as e:
            print(str(e))
            await ctx.send(ctx.author.mention + ', You don\'t have any coins, hints, or saves! Type `$start` to start a hangman game, and win to gain coins!')
@client.command(aliases=["add-coins"])
async def add_coins(ctx, add_coins):
    def check(author):
        def inner_check(message): 
            if ctx.author != author:
                return False
            return True
        return inner_check
    if ctx.author.id != 697628625150803989 and ctx.author.id != 713467569725767841 and ctx.author.id != 738111431152500796:
        return await ctx.send('You must own the bot to use this command!')
    if creds.access_token_expired:
        gs_client.login()
    sheet = gs_client.open('Hangman bot').sheet1
    try:
        add_coins = str(add_coins)
        add_coins = int(add_coins)
    except NameError as e:
        await ctx.send('Enter a number!')
        print(str(e))
        return

    if len(ctx.message.mentions):
        try:
            cell = sheet.find(str(ctx.message.mentions[0].id))
            column = cell.col + 1
            print(column)
            print(cell.col)
            coins = sheet.cell(cell.row, column).value
            coins = str(coins)
            coins = int(coins)
            coins += add_coins
            sheet.update_cell(cell.row, column, coins)
        except Exception as e:
            print(e)
            row = [ctx.message.mentions[0].id, add_coins, 0, 0, 0]
            index = sheet.row_count + 1
            sheet.insert_row(row, index)
        await ctx.send('Success!')
    else:
        await ctx.send('Enter a user!')
        return
@client.command(aliases=["remove-coins"])
async def remove_coins(ctx, add_coins):
    if ctx.author in authors:
        return
    def check(author):
        def inner_check(message): 
            if ctx.author != author:
                return False
            return True
        return inner_check
    if ctx.author.id != 697628625150803989 and ctx.author.id != 713467569725767841 and ctx.author.id != 738111431152500796:
        return await ctx.send('You must own the bot to use this command!')
    if creds.access_token_expired:
        gs_client.login()
    sheet = gs_client.open('Hangman bot').sheet1
    await ctx.send('How many coins should I remove?')
    try:
        add_coins = str(add_coins)
        add_coins = int(add_coins)
    except Exception as e:
        await ctx.send('Enter a number!')
        print(str(e))
        return

    if len(ctx.message.mentions):
        try:
            cell = sheet.find(str(ctx.message.mentions[0].id))
            column = cell.col + 1
            print(column)
            print(cell.col)
            coins = sheet.cell(cell.row, column).value
            coins = str(coins)
            coins = int(coins)
            coins -= add_coins
            sheet.update_cell(cell.row, column, coins)
        except Exception as e:
            print(e)
            await ctx.send('This user doesn\'t have any coins!')
        await ctx.send('Success!')
    else:
        await ctx.send('Enter a user!')
        return
@client.command(aliases=["buy-hint"])
async def buy_hint(ctx):
    await ctx.send('Hello! This command was recently changed to `$buy hint` instead of `$buy-hint`! ')
@client.command()
async def buy(ctx, item):
    if ctx.author in authors:
        return
    if item == 'hint':
        await ctx.send('Giving you a hint...')
        if creds.access_token_expired:
            gs_client.login()
        sheet = gs_client.open('Hangman bot').sheet1
        try:
            cell = sheet.find(str(ctx.author.id))
            column = cell.col + 1
            column_h = cell.col + 2
            coins = sheet.cell(cell.row, column).value
            hints = sheet.cell(cell.row, column_h).value
            coins = str(coins)
            coins = int(coins)
            hints = str(hints)
            hints = int(hints)
            if coins < 5:
                return await ctx.send('You don\'t have enough coins!')
            coins -= 5
            hints += 1
            sheet.update_cell(cell.row, column, coins)
            sheet.update_cell(cell.row, column_h, hints)
            await ctx.send('Success! You now have one more hint!')
        except Exception as e:
            print(e)
            await ctx.send('You don\'t have any coins! Get coins by typing `$start` and win!')
    # Below is a new currency which has not been released yet
    elif item == 'defenition' or item == 'def':
        await ctx.send('Giving you a defenition...')
        if creds.access_token_expired:
            gs_client.login()
        sheet = gs_client.open('Hangman bot').sheet1
        try:
            cell = sheet.find(str(ctx.author.id))
            column = cell.col + 1
            column_d = cell.col + 4
            coins = sheet.cell(cell.row, column).value
            defenitions = sheet.cell(cell.row, column_d).value
            coins = str(coins)
            coins = int(coins)
            defenitions = str(defenitions)
            defenitions = int(defenitions)
            if coins < 7:
                return await ctx.send('You don\'t have enough coins!')
            coins -= 5
            defenitions += 1
            sheet.update_cell(cell.row, column, coins)
            sheet.update_cell(cell.row, column_d, defenitions)
            await ctx.send('Success! You now have one more hint!')
        except Exception as e:
            print(e)
            await ctx.send('You don\'t have any coins! Get coins by typing `$start` and win!')
@client.command()
async def shop(ctx):
    if ctx.author in authors:
        return
    hex_number = random.randint(0,16777215)
    shopEmbed = discord.Embed(title='Shop', color=hex_number)
    shopEmbed.add_field(name='Hints', value='**Cost**: 5 coins\n**How to buy:** `$buy hint`\n**How to use:** When you are in the middle of a game, type "hint" instead of a letter to use.\n**Effects:** Reveals one letter of the word for you!')
    shopEmbed.add_field(name='Saves', value='**Cost**: Can only be obtained by [giveaways](https://discord.gg/CRGE5nF) or by voting (see `$vote`)\n**How to use:** When you are in the middle of a game, type "save" instead of a letter to use.\n**Effects:** Gives you an extra try!!')
    shopEmbed.timestamp = datetime.datetime.now()
    shopEmbed.set_footer(text='More things coming soon!')
    await ctx.send(embed=shopEmbed)
@client.command()
async def vote(ctx):
    if ctx.author in authors:
        return
    hex_number = random.randint(0,16777215)
    voteEmbed = discord.Embed(title='Vote for Aadit\'s Hangman Bot!', color=hex_number)
    voteEmbed.add_field(name="2 saves per vote (bot)", value="[Top.gg](https://top.gg/bot/748670819156099073)\n[Discord Boats](https://discord.boats/bot/748670819156099073)\n[DBL](https://discord.ly/aadits-audits-hangman-bot)")
    voteEmbed.add_field(name="No perks, but please vote (bot)", value="[Botrix.cc](https://botrix.cc/bots/748670819156099073)\n[RBL](https://bots.rovelstars.ga/bots/748670819156099073)")
    voteEmbed.add_field(name="No voting system", value="[discord.bots.gg](https://discord.bots.gg/bots/748670819156099073)\n[BOD](https://bots.ondiscord.xyz/bots/748670819156099073)")
    voteEmbed.add_field(name='Vote for our server!', value='[top.gg](https://top.gg/servers/748672765837705337)')
    voteEmbed.timestamp = datetime.datetime.now()
    voteEmbed.set_footer(text='TYSM for voting!')
    await ctx.send(embed=voteEmbed)
@client.command()
async def servers(ctx):
    if ctx.author in authors:
        return
    servers = list(client.guilds)
    await ctx.send(f"I am currently in {str(len(servers))} servers!")
@client.command()
async def load(ctx):
    client.load_extension('topGG')
    await ctx.send('Done')
@client.command()
async def post(ctx):
    if ctx.author.id == 697628625150803989:
        webs = ['discord.boats', 'top.gg', 'discordbotlist.com']
        data = ""
        for web in webs:
            if web == 'discord.boats' or web == 'top.gg':
                param_name = 'server_count'
                if web == 'discord.boats':
                    auth = os.environ['discord.boats-token']
                    url = 'https://discord.boats/api/bot/748670819156099073'
                elif web == 'top.gg':
                    auth = os.environ['top.gg-token']
                    url = 'https://top.gg/api/bots/748670819156099073/stats'
            elif web == 'discordbotlist.com':
                param_name = 'guilds'
                auth = os.environ['discordbotlist.com-token']
                url = 'https://discordbotlist.com/api/v1/bots/748670819156099073/stats'
            body = {param_name: len(client.guilds)}
            headers = {'Authorization': auth}
            r = requests.post(url, data=body, headers=headers)
            data += f'{web}:\n```{r.json()}```\n'
        await ctx.send(f'Posted server count! Results:\n\n{data}')
@client.command()
async def pay(ctx, member: discord.Member, amount):
    await ctx.send('Paying money...')
    try:
        amount = int(amount)
    except:
        return await ctx.send('The amount must be an integer!')
    if creds.access_token_expired:
        gs_client.login()
    sheet = gs_client.open('Hangman bot').sheet1
    try:
        cell = sheet.find(str(ctx.author.id))
        column = cell.col + 1
        print(column)
        print(cell.col)
        coins = sheet.cell(cell.row, column).value
        coins = str(coins)
        coins = int(coins)
        if coins < amount:
            return await ctx.send('You don\'t have that much coins!')
        coins -= amount
        sheet.update_cell(cell.row, column, coins)
    except Exception as e:
        print(e)
        await ctx.send('You don\'t have that much coins!')
    try:
        cell = sheet.find(str(member.id))
        column = cell.col + 1
        print(column)
        print(cell.col)
        coins = sheet.cell(cell.row, column).value
        coins = str(coins)
        coins = int(coins)
        coins += amount
        sheet.update_cell(cell.row, column, coins)
    except Exception as e:
        print(e)
        row = [member.id, amount, 0, 0, 0]
        index = sheet.row_count + 1
        sheet.insert_row(row, index)  
    await ctx.send(f'Successfully gave {member.mention} {amount} coins!')
@client.command()
async def rich(ctx):
    hex_number = random.randint(0,16777215)
    richEmbed = discord.Embed(title='Rich', color=hex_number)
    if ctx.author in authors:
        return
    await ctx.send('Getting richest users...')
    if creds.access_token_expired:
        gs_client.login()
    sheet = gs_client.open('Hangman bot').sheet1
    users = sheet.col_values(1)
    coins = sheet.col_values(2)
    users.pop(0)
    coins.pop(0)
    for amount in coins:
        coins[coins.index(amount)] = int(amount)
    for x in range(5): 
        try:
            coinsadd = max(coins)
            i = coins.index(coinsadd)
            useradd = await client.fetch_user(users[i])
            coins.pop(i)
            users.pop(i)
            leader = "%d: %s" % (x + 1, useradd.name)
            embedtext = "%s coins" % (coinsadd)
            richEmbed.add_field(name=leader, value=embedtext)
        except ValueError as e:
            print("The list of coins length < 5")
    richEmbed.set_footer(text='Credit for this command goes to CodeMyGame#0923')
    await ctx.send(embed=richEmbed)   
        

client.run(os.environ['token'])