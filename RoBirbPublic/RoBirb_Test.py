#Imports
from inspect import getclosurevars
import time
import random
import datetime
import re
import importlib
import discord
from discord.channel import DMChannel
from discord.message import MessageReference
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
import pymongo
import asyncio
from pymongo import MongoClient
from bson.objectid import ObjectId
import FUNCTIONS

#The big mamba jamba himself

#Important stuff and bot initialisation
token = "ha no"
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f'{client.user} is online')
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Why hello there"))


#MongoDB Initialisation
mongoClient = MongoClient('')
db = mongoClient.doWhatYouWant
currencyDB = db.currency 
serverDB = db.servers
dmDB = db.directMessages 
workDB = db.schedRequests
invDB = db.inventory
christmasDB = db.christmasy
gambleDB = db.gambling


#Setup
ownerID = 1273
prefix = '$'
currency = 'money'
botName = 'whatever you want it to be'
christmas = False


#All bot command trees
@client.event
async def on_message(message):
    #direct message response tree, and makes sure the bot doesn't respond to commands through DM's
    if isinstance(message.channel, discord.DMChannel) and message.author != client.user:
            print ('\nNew DM from: ', message.author, ' (',message.author.id,') at: ', datetime.datetime.now(), '\nContent: ', message.content, '\nUploaded to directMessage database')
            await message.channel.send('Hippidy hoppidy you are now my property')
            dmDB.insert_one({"author": message.author.name,
                             "discriminator": message.author.discriminator,
                             "authorID": message.author.id,
                             "client": client.user,
                             "messageContent": message.content,
                             "time": datetime.datetime.now()})
            return
    elif isinstance(message.channel, discord.DMChannel) and message.author == client.user:
        return
    else:
        #All bot command trees. For real this time

        #server specific prefix setup
        if serverDB.find_one({"serverID": message.guild.id}) == None:
            prefix = '$'
        else:
            prefix = serverDB.find_one({"serverID": message.guild.id})["prefix"]

        #Makes sure the bot doesn't respond to its own messages
        if message.author == client.user:
            return

        #status command tree
        elif message.content.startswith(prefix+'status'):
            if message.author.id != ownerID:
                return
            else:
                await client.change_presence(status=discord.Status.idle, activity=discord.Game(message.content[7+len(prefix):]))
                await message.delete()

        #hello command tree
        elif message.content.startswith(prefix+'hello'):
            await message.channel.send('Hello!')
            
        #dmme command tree
        elif message.content.startswith(prefix+'dmme'):
            await message.author.send("hi")

        #echo command tree
        elif message.content.startswith(prefix+'echo'):
            length = 4 + len(prefix)
            text = message.content
            await message.channel.send(text[length:])

        #test command tree
        elif message.content.startswith(prefix+'test'):
            content = message.content.split()
            if 'hello' in message.content.lower():
                await message.channel.send('hello there')
            elif 'hi' in message.content.lower():
                await message.channel.send('hi there')
            elif 'shrubbery' in message.content.lower():
                await message.channel.send('bush')
            elif 'test' == content[1]:
                await message.channel.send('testing')
            elif (message.content.lower())[5+len(prefix):10+len(prefix)] == 'penis':
                await message.channel.send('shlong')
            else:
                await message.channel.send((message.content)[(4+len(prefix)):])

        #serversetup command tree
        elif message.content.startswith(prefix+'serversetup'):
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverDB.insert_one({"serverID": message.guild.id,
                                         "prefix": prefix,
                                         "verificationRole": "",
                                         "botSpamChannel": "",
                                         "suggestionChannel": "",
                                         "welcomeChannel": "",
                                         "joinMessage": "",
                                         "leaveMessage": "",
                                         "muteRole": ""})
                    await message.channel.send('A record has been setup for this server in my database. The only data recorded is the server ID. You can add other data as well (custom prefix, verification role, bot spam channel). You can get your servers data with `serverdata`')
                else:
                    await message.channel.send('There are already records setup for this server.')
            else:
                return

        #setrole command tree
        elif message.content.startswith(prefix+'setrole'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('There are no records setup for this server. Please run the `serversetup` command')
                    return
                else:
                    if 'verification' in content[1]:
                        ping = content[2]
                        if ping != '' and ping:
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"verificationRole": ping}})
                            sendMessage = 'The verification role of this server has been updated to: '+str(serverDB.find_one({"serverID": message.guild.id})["verificationRole"])
                            await message.channel.send(ping)
                        else:
                            await message.channel.send('Please input a role to set as the verification role.')
                    else:
                        await message.channel.send('Please input a valid subcommand.')
            else:
                return
                    
        #setprefix command tree
        elif message.content.startswith(prefix+'setprefix'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('There are no records setup for this server. Please run the `serversetup` command')
                else:
                    if content[1] == '':
                        sendMessage = 'The prefix for me in this server is '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"])
                        await message.channel.send(sendMessage)
                    else:
                        serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"prefix": content[2]}})
                        sendMessage = 'The prefix for me in this server has now been updated to '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"])
                        await message.channel.send(sendMessage)
            else:
                return

        #serverdata command tree
        elif message.content.startswith(prefix+'serverdata'):
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) != None:
                    await message.channel.send('The data that is recorded for your server on my database:')
                    await message.channel.send(serverDB.find_one({"serverID": message.guild.id}))
                else:
                    await message.channel.send('No records found')
            else:
                return

        #deleteserverdata command tree
        elif message.content.startswith(prefix+'deleteserverdata'):
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('No records found')
                else:
                    await message.channel.send('This action is irreversible. Do you wish to proceed? Y/N')
                    workDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "deleteSData",
                                       "timeLeft": 10,
                                       "bot": client.user.id})
            else:
                return
        elif workDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "deleteSData"}) != None:
            content = message.content.split()
            if content[0].lower() == 'y' or content == 'yes': 
                serverDB.find_one_and_delete({"serverID": message.guild.id})
                workDB.find_one_and_delete({"userID": message.author.id})
                await message.channel.send('Operation sucessfull')
            else:
                await message.channle.send('Operation failure')
                           
        #verify command tree
        elif message.content.startswith(prefix+'verify'):
            await message.author.add_roles(message.guild.get_role(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": message.guild.id})["verificationRole"])))), reason='USER VERIFICATION')
            sendMessage = 'You have now been verified in '+message.guild.name+'. Enjoy the server!'
            await message.author.send(sendMessage)
            await message.delete()

        #uverify command tree
        elif message.content.startswith(prefix+'uverify'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if content[1] == '':
                    await message.delete()
                    return
                else:
                    await message.mentions[0].add_roles(message.guild.get_role(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": message.guild.id})["verificationRole"])))), reason='USER VERIFICATION')
                    await message.delete()

        #setchannel command tree
        elif message.content.startswith(prefix+'setchannel'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('There are no records set up for this server. Please run the `serversetup` command')
                else:
                    if content[1] == 'botspam':
                        if message.content[len(prefix)+19:] == '':
                            await message.channel.send('Please mention a channel to set as the bot spam')
                        else:
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"botSpamChannel": content[2]}})
                            sendMessage = 'My bot spam channel for this server has been updated to:'+str(serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"])
                            await message.channel.send(sendMessage)
                    elif content[1] == 'welcome':
                        if message.content[len(prefix)+19:] == '':
                            await message.channel.send('Please mention a channel to set as the bot spam')
                        else:
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"welcomeChannel": content[2]}})
                            await message.channel.send('My welcome channel for this server has been updated to:'+str(serverDB.find_one({"serverID": message.guild.id})["welcomeChannel"]))
                    else:
                        await message.channel.send('Please input a valid subcommand')
            else:
                return

        #member setup command tree
        elif message.content.startswith(prefix+'setup'):
            if currencyDB.find_one({"userID": message.author.id}) == None and invDB.find_one({"userID": message.author.id}) == None:
                currencyDB.insert_one({"userID": message.author.id,
                                       "levelXP": 0,
                                       "birbSeed": 0,
                                       "canDoDaily": 1,
                                       "nextDaily": ""})
                invDB.insert_one({"userID": message.author.id, "items": 0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0})
                await message.channel.send('You have been added to our database. Use the `bank` command to check your, well, bank')
            elif currencyDB.find_one({"userID": message.author.id}) != None and invDB.find_one({"userID": message.author.id}) == None:
                invDB.insert_one({"userID": message.author.id, "items": 0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0})
                await message.channel.send('You have been added to our database. Use the `bank` command to check your, well, bank')
            elif currencyDB.find_one({"userID": message.author.id}) == None and invDB.find_one({"userID": message.author.id}) != None:
                currencyDB.insert_one({"userID": message.author.id,
                                       "birbSeed": 0,
                                       "canDoDaily": 1,
                                       "nextDaily": ""})
                await message.channel.send('You have been added to our database. Use the `bank` command to check your, well, bank')
            else:
                await message.channel.send("We already have records of your existance. We don't need anymore")

        #daily command tree
        elif message.content.startswith(prefix+'daily'):
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("Do the `setup` command. You arn't on my database")
            elif workDB.find_one({"userID": message.author.id, "action": "daily"}) != None:
                timeLeft = workDB.find_one({"userID": message.author.id, "action": "daily"})["timeLeft"]
                seconds = timeLeft % (24 * 3600)
                hour = seconds // 3600
                seconds = seconds % 3600
                minutes = seconds // 60
                seconds = seconds % 60
                await message.channel.send("Too soon! You cannot get a daily draw again for another "+str(hour)+':'+str(minutes)+':'+str(seconds))
            else:
                ammount = random.randint(1, 5000)
                prevAmmount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                updatedAmmount = ammount+prevAmmount
                currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                await message.channel.send("You won "+str(ammount)+" "+currency+" from your daily draw! Come back in 24 hours to get more! \nYou now have "+str(updatedAmmount)+" "+currency)
                workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "daily",
                                   "timeLeft": 86400,
                                   "bot": client.user.id})
                
        #bank command tree
        elif message.content.startswith(prefix+'bank'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send('What bank? I have no idea who you are. Do `setup`')
            elif 'balance' == content[1]:
                if message.content[len(prefix)+4:] == '': 
                    await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency)
                else:
                    ping = message.mentions[0]
                    if ping.id == message.author.id:
                        await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency+'\nYou dont need to ping yourself to find out your balance btw')
                    elif currencyDB.find_one({"userID": ping.id}) == None:
                        await message.channel.send('I cannot find that person in my database')
                    else:
                        await message.channel.send('They have '+str(currencyDB.find_one({"userID": ping.id})["birbSeed"])+' '+currency)
            elif 'transfer' == content[1]:
                ping = message.mentions[0]
                if content[2] == '':
                    await message.channel.send("Who do you want to transfer to? \nIf you ping nobody, I should just take the money for myself")
                    return
                elif ping.id == message.author.id:
                    await message.channel.send("You can't transfer money to yourself. \nI thought that would be kinda obvious")
                    return
                elif currencyDB.find_one({"userID": ping.id}) == None:
                    num = random.randint(0,4)
                    if num == 1:
                        await message.channel.send('I am unable to find your friend in my database! Ask them politely to do the `setup` command')
                    elif num == 2:
                        await message.channel.send('I am unable to find your friend in my database! Nag them to do the `setup` command')
                    elif num == 3:
                        await message.channel.send('I am unable to find your friend in my database! Shout at them to do the `setup` command')
                    else:
                        await message.channel.send("Err: witty response not found. \nOh yeah, your friend isn't in my database. Tell 'em to do the `setup` command")
                else:
                    ammount = content[3]
                    if ammount == '':
                        await message.channel.send("Nothing isn't a form of currency I'm programmed to support")
                        return
                    elif ammount.isdigit():
                        if int(ammount) <= 0:
                            await message.channel.send("You either don't understand money, or you're cheap. \nOr the person owes you money \nEither way, I'm not doing that")
                            return
                        else:
                            if currencyDB.find_one({"userID": message.author.id})["birbSeed"] < int(ammount):
                                await message.channel.send("You don't have enough money for this operation. And I ain't supplying it to you")
                                return
                            else:
                                pingAmmount = currencyDB.find_one({"userID": ping.id})["birbSeed"]
                                updatedPingAmmount = pingAmmount+int(ammount)
                                currencyDB.find_one_and_update({"userID": ping.id},{"$set":{"birbSeed": updatedPingAmmount}})
                                authorAmmount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                updatedAuthorAmmount = authorAmmount-int(ammount)
                                currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAuthorAmmount}})
                                pingID = str(ping.id)
                                if int(ammount) < 100:
                                    sendMessage = 'You just gave '+ammount+' '+currency+' to <@'+str(pingID)+'>! How *generous*'
                                else:
                                    sendMessage = 'You just gave '+ammount+' '+currency+' to <@'+str(pingID)+'>! How generous!'
                                await message.channel.send(sendMessage)
                    else:
                        await message.channel.send("Either something went wrong, or you're trying to transfer somebody a word. \nThat's what DM's are for")
            else:
                await message.channel.send('Please input a valid subcommand')

        #work command tree
        elif message.content.startswith(prefix+'work'):
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You want to do payless work? That's fine by me. \nYou don't have a bank to put money into. Do `setup`")
            elif workDB.find_one({"userID": message.author.id, "action": "work"}) != None:
                await message.channel.send("You already have a work request set up. Pick a number between 1 and 5.")
            elif workDB.find_one({"userID": message.author.id, "action": "workTimer"}) != None :
                timeLeft = workDB.find_one({"userID": message.author.id, "action": "workTimer"})["timeLeft"]
                seconds = timeLeft % (24 * 3600)
                hour = seconds // 3600
                seconds = seconds % 3600
                minutes = seconds // 60
                seconds = seconds % 60
                await message.channel.send("Too soon! You cannot work again for another "+str(hour)+':'+str(minutes)+':'+str(seconds))
            else:
                workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "work",
                                   "timeLeft": 10,
                                   "bot": client.user.id})
                await asyncio.sleep(0.1)
                await message.channel.send("Pick a number between 1 and 5")
        elif workDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "work"}) != None:
            content = message.content.split()
            if content[0] == '1' or '2' or '3' or '4' or '5':
                num = random.randint(0,5)
                if content[0] == '1':
                    if num == 1:
                        num2 = random.randint(100,1000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 2:
                        num2 = random.randint(1,5000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 3:
                        num2 = random.randint(500, 2500)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 4:
                        num2 = random.randint(0, 10000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 5:
                        num2 = random.randint(1000, 50000)
                        if num2 == 20765:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+1000000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won the jackpot! An aditional 100k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        else:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                elif content[0] == '2':
                    if num == 1:
                        num2 = random.randint(300, 6900)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 2:
                        num2 = random.randint(100,1000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 3:
                        num2 = random.randint(250, 10000)
                        if num2 == 517:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+100000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! On your way home, you got a scratch card and won! An aditional 10k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "workTimer",
                                       "timeLeft": 10800,
                                       "bot": client.user.id})
                        else:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "workTimer",
                                       "timeLeft": 10800,
                                       "bot": client.user.id})
                    elif num == 4:
                        num2 = random.randint(500, 25000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 5:
                        num2 = random.randint(10, 500)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                elif content[0] == '3':
                    if num == 1:
                        num2 = random.randint(5, 250)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 2:
                        num2 = random.randint(250, 1500)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 3:
                        num2 = random.randint(500, 6000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 4:
                        num2 = random.randint(690, 10000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 5:
                        num2 = random.randint(250, 1500)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                elif content[0] == '4':
                    if num == 1:
                        num2 = random.randint(420, 69000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 2:
                        num2 = random.randint(782, 12635)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 3:
                        num2 = random.randint(850,9000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 4:
                        num2 = random.randint(500, 40000)
                        if num2 == 36841:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+1000000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won the jackpot! An aditional 100k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 == 27340 or 39666:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+75000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 75k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 == 34474 or 20714 or 12502:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+50000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 50k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 == 11294 or 5112 or 20033 or 38827 or 21014:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+25000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 25k has been added to your bank"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        else:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                            await message.channel.send(sendMessage)
                            workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 5:
                        num2 = random.randint(1000, 75000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                elif content[0] == '5':
                    if num == 1:
                        num2 = random.randint(250, 2500)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 2:
                        num2 = random.randint(10000, 100000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 3:
                        num2 = random.randint(0, 250)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 4:
                        num2 = random.randint(500, 5000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                    elif num == 5:
                        num2 = random.randint(420, 42000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                else:
                    await message.channel.send("Something went wrong. I don't know what. Chances are, the dev doesn't either")
                    workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
            else:
                await message.channel.send("You haven't entered a number matching the criteria")
                workDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                return
        
        #easier bank balance command
        elif message.content.startswith(prefix+'bal'):
            if message.content[len(prefix)+4:] == '': 
                if currencyDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send('What bank? I have no idea who you are. Do `setup`')
                else:
                    await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency)
            else:
                ping = message.mentions[0]
                if ping.id == message.author.id:
                    if currencyDB.find_one({"userID": message.author.id}) == None:
                        await message.channel.send('What bank? I have no idea who you are. Do `setup`')
                    else:
                        await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency+'\nYou dont need to ping yourself to find out your balance btw')
                elif currencyDB.find_one({"userID": ping.id}) == None:
                    await message.channel.send('I cannot find that person in my database')
                else:
                    await message.channel.send('They have '+str(currencyDB.find_one({"userID": ping.id})["birbSeed"])+' '+currency)

        #shop command tree
        elif message.content.startswith(prefix+'shop'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You have no bank with which to pay for things. \nI'm not giving them to you for free \n`"+prefix+"setup`")
            elif message.content[5+len(prefix):] == '':
                await message.channel.send("Please input a valid subcommand")
            elif 'inventory' == content[1] or 'inv' == content[1]:
                if message.content[16:] == '' or message.content[16:] == '1':
                    #Page 1
                    embed = discord.Embed(title = "__Shop Contents__", description="Do `"+prefix+"shop item {number}` to find out about the item", colour = 0xFA00FF)
                    for i in range(1,12):
                        embed.add_field(name=str(i)+': '+invDB.find_one({"list":"name"})[str(i)], value= invDB.find_one({"list":"price"})[str(i)])
                    embed.set_footer(text="Page 1")
                    await message.channel.send(embed=embed)
                #else:
            elif 'item' == content[1]:
                if message.content[len(prefix)+10:] == '':
                    await message.channel.send("Please input a valid item number")
                elif '1' == content[2]:
                    embed = discord.Embed(title = "__Lolipop__", description = "A cheap and very pleasant food. Costs 50 "+currency, colour = 0xFFA500)
                    #embed.set_image(url='https://i.imgur.com/qMdwyYJ.png')
                    #embed.add_field(name='More Info',value='Heals 5 health. Grants the user a "sugar-rush" which increases their attack speed for 1 move',inline=True)
                    #embed.set_footer(text='No copyright infringement intended with the image')
                    await message.channel.send(embed=embed)
                elif '2' == content[2]:
                    embed = discord.Embed(title = "__Stick__", description = "You could always just pick up some random stick off the floor, but this is a PREMIUM stick, made out of the *finest* quality wood! It is guaranteed to give you MAXIMUM STICK POWER! Costs 100 "+currency, colour=0xFFA500)
                    embed.add_field(name='More Info', value="A literal stick. It seems like it could be pretty useful for whacking people. A small part of you feels like the end of this stick would be a good home for a jalapeno.")
                    #embed.set_image(url='https://i.imgur.com/6XeKbdg.jpg')
                    #embed.set_footer(text='No copyright infringement intended with the image')
                    await message.channel.send(embed=embed)
                elif '3' == content[2]:
                    embed = discord.Embed(title = "__Cane__", description = "A piece of wood with a handle on top. Could be used to make walking easier. Could also be used to hit somebody. Costs 250 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '4' == content[2]:
                    embed = discord.Embed(title = "__A Butter Knife__", description = "A relatively un-sharp and inexpensive knife. If enough force is put behind it, it could, in theory, be used as a weapon. Costs 400 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '5' == content[2]:
                    embed = discord.Embed(title = "__A Doughnut__", description = "A sugary treat. A circular piece of dough with a whole in the middle, with icing and toppings on top. Costs 350 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '6' == content[2]:
                    embed = discord.Embed(title = "__A Pack Of Doughnuts__", description = "A pack of 3 doughnuts. What did you expect? Costs 700 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '7' == content[2]:
                    embed = discord.Embed(title = "__Fait 600__", desctription = "A vehicle. Seems like it would be much faster than regular movement, but would require tires every now and then. Costs 600 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '8' == content[2]:
                    embed = discord.Embed(title = "__Tire__", description = "A Tire. It seems around the right size to fit on a Fait 600. Costs 150 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '9' == content[2]:
                    embed = discord.Embed(title = "__Chair__", description = "A wooden chair. It looks comfortable! Also looks capable of incapitating somebody if you hit them with it hard enough. Costs 1000 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '10' == content[2]:
                    embed = discord.Embed(title = "__Human__", description = "A human male. He will protect you if you get into a sticky situation. He does require sustinance, however. And can only handle so much. Costs 1500 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed=embed)
                elif '11' == content[2]:
                    embed = discord.Embed(title = "__Set Of Wheels__", description = "Wheels. These will make you the coolest, most blinged out ~~motherf~~-person on the streets. Guarenteed to increase speed by 5%, and chance of being robbed by 50%. Costs 1250 "+currency, colour = 0xFFA500)
                    await message.channel.send(embed-embed)
                else:
                    await message.channel.send('Please enter a valid item number')
            elif 'buy' == content[1]:
                if message.content[len(prefix)+9:] == '':
                    await message.channel.send("Please provide a valid item number to buy")
                    return
                num = 0
                for a in range(1,12):
                    if str(a) == content[2]:
                        if message.content[len(prefix)+len(content[0])+len(content[1])+len(content[2])+1:] == '':
                            c = 1
                        elif content[3].isdecimal == True:
                            c = int(content[3])
                        else:
                            c = int(content[3])
                        if str(a) == "6":
                            i = 5
                            b = (3*c)
                        else:
                            i = a
                            b = c
                        bankBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        price = invDB.find_one({"list": "price"})[str(a)]
                        if int(bankBal) < int(int(price)*c):
                            await message.channel.send("You can't afford that.")
                        else:
                            newBal = int(bankBal) - int(int(price)*c)
                            if invDB.find_one({"userID": message.author.id}) == None:
                                invDB.insert_one({"userID": message.author.id, "items": 0})
                                for a in range(1,24):
                                    invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(a): 0}})
                            items = invDB.find_one({"userID": message.author.id})["items"]
                            if invDB.find_one({"userID": message.author.id})[str(i)] == None:
                                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(i): b}})
                                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{"items": items+b}})
                            else:
                                num = invDB.find_one({"userID": message.author.id})[str(i)]
                                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(i): (num+b)}})
                                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{"items": items+b}})
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                            name = invDB.find_one({"list": "name"})[str(a)]
                            await message.channel.send("You just bought "+str(c)+" "+name.lower()+"! You now have "+str(newBal)+" "+currency)
                    else:
                        num += 1
                if num == 12:
                    await message.channel.send("Please provide a valid item number to buy")
            elif 'sell' == content[1]:
                if message.content[len(prefix)+10:] == '':
                    await message.channel.send("Please provide an item number to sell")
                else:
                    for i in range(1,24):
                        if content[2] == str(i):
                            if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                await message.channel.send("You don't own any of this item. In which case, you cannot sell it")
                            else:
                                #await message.channel.send(message.content[(len(prefix)+len(str(content[2]))+10):])
                                if message.content[(len(prefix)+len(str(content[2]))+11):] == "":
                                    num = 87982388927
                                elif content[3].isdecimal() == True:
                                    num = int(content[3])
                                else: num = 1
                                amount = invDB.find_one({"userID": message.author.id})[str(content[2])]
                                if amount < num:
                                    await message.channel.send("You don't have the required amount of items. And you cannot sell air")
                                else:
                                    invDB.find_one_and_update({"userID": message.author.id},{"$set":{str(content[2]):(amount-num)}})
                                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                    num2 = invDB.find_one({"list": "price"})[str(content[2])]
                                    amount2 = int((int(num2)*int(num))/2)
                                    currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": (prevBal+amount2)}})
                                    name = invDB.find_one({"list": "name"})[str(content[2])]
                                    await message.channel.send("You have successfully sold "+str(num)+" "+name+"!\nYou have earned "+str(amount2)+" "+currency)

        #help command tree
        elif message.content.startswith(prefix+'help'):
            content = message.content.split()
            embed = discord.Embed(title = "__**Welcome to the new RoBirb!**__", description = "I have been under development for quite a while. But that time was spent productively, however. I have many many new features")
            embed.add_field(name='__Moderation Features__', value=prefix+'help moderation', inline=True)
            embed.add_field(name='_Currency Features_', value=prefix+'help currency', inline=True)

        #killme command tree
        elif message.content.startswith(prefix+'killme'):
            await message.channel.send("-shoots the mcshit out of <@"+str(message.author.id)+">-")
            
        #kill command tree
        elif message.content.startswith(prefix+'kill'):
            content = message.content.split()
            if message.content[5+len(prefix):] == '':
                await message.channel.send('<@'+str(message.author.id)+'> kills the air!')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> kills <@'+str(message.mentions[0].id)+'>')
                
        #slaughter command tree
        elif message.content.startswith(prefix+'slaughter'):
            content = message.content.split()
            if message.content[len(prefix)+10:] == '':
                await message.channel.send('<@'+str(message.author.id)+'> brings down an absolute masacare onto the air molecules!')
            elif message.mentions[0].id == ownerID and message.author.id == ownerID:
                await message.channel.send("My owner is trying to slaughter himself? \nGuess I'm going back to updaten't!")
            elif message.mentions[0].id == ownerID and message.author.id != ownerID:
                await message.channel.send('<@'+str(message.author.id)+'> tries to slaughter <@'+str(ownerID)+'> but, with him being my developer, it is in my best interest to keep him alive. \n-slaughters <@'+str(message.author.id)+'> btw- :)')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> brings down an absolute masacare onto <@'+str(message.mentions[0].id)+'>')
                
        #hug command tree
        elif message.content.startswith(prefix+'hug'):
            content = message.content.split()
            if message.content[4+len(prefix):] == '':
                await message.channel.send('-Gives <@'+str(message.author.id)+'> a big robotic hug-')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> gives <@'+str(message.mentions[0].id)+'> a big hug!')
                
        #punch command tree
        elif message.content.startswith(prefix+'punch'):
            content = message.content.split()
            if message.content[6+len(prefix):] == '':
                await message.channel.send('-punches <@'+str(message.author.id)+'>-')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> punches <@'+str(message.mentions[0].id)+'>!')
                
        #kiss command tree
        elif message.content.startswith(prefix+'kiss'):
            content = message.content.split()
            if message.content[4+len(prefix):] == '':
                await message.channel.send('I\'ll take a pass on this one')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> gives <@'+str(message.mentions[0].id)+'> a kiss!')
                
        #rps command tree
        elif message.content.startswith(prefix+'rps'):
            content = message.content.split()
            if message.content[len(prefix)+3:] == '':
                await message.channel.send("__Rock Paper Scissors__ \nIt's literally just rock paper scissors. Rock beats scissors, paper beats rock and scissors beats paper. \nIf you win the game, you get 2x what you put in \nUsage: `"+prefix+"rps {'r'. 'p' or 's'} {ammount}`")
            elif content[1] == 'help':
                await message.channel.send("__Rock Paper Scissors__ \nIt's literally just rock paper scissors. Rock beats scissors, paper beats rock and scissors beats paper. \nIf you win the game, you get 2x what you put in \nUsage: `"+prefix+"rps {'r'. 'p' or 's'} {ammount}`")
            elif currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You can't gamble when you dont have a bank to get the money from \n`"+prefix+"setup`")
            elif content[2] == '' or content[2].isdecimal() == False:
                await message.channel.send("Please provide an ammount to gamble with")
            elif int(content[2]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                await message.channel.send("You have insufficient funds for the operation")
            elif int(content[2]) == 0:
                await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
            else:
                rps = 0
                rps2 = 0
                number = random.randint(1,3)
                if number == 1:
                    rps = 1
                elif number == 2:
                    rps = 2
                elif number == 3:
                    rps = 3
                else:
                    #Should hopefully never need to be called, but just in case.
                    await message.channel.send("I'm sorry, but something has gone very wrong. \nThe dev has been notified")
                    print ('Fatal error in guild: '+str(message.guild.id)+'\nBot: '+botName+' ('+str(client.user)+'\nrps command tree')
                    return
                if content[1] == 'r':
                    rps2 = 1
                elif content[1] == 'p':
                    rps2 = 2
                elif content[1] == 's':
                    rps2 = 3
                else:
                    await message.channel.send("Incorrect command usage")
                if rps == rps2:
                    await message.channel.send("Draw")
                elif rps == 1:
                    if rps2 == 3:
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        if prevBal >= 10000000:
                            win = int(int(content[2])/(prevBal/10000000))
                        else:
                            win = int(content[2])
                        newBal = prevBal+win
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                        await message.channel.send("You win \n"+str(win)+" "+currency+" has been added to your bank")
                    elif rps2 == 2:
                        await message.channel.send("You lose \n"+content[2]+" "+currency+' has been withdrawn from your bank')
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        newBal = prevBal-int(content[2])
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                elif rps == 2:
                    if rps2 == 1:
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        if prevBal >= 10000000:
                            win = int(int(content[2])/(prevBal/10000000))
                        else:
                            win = int(content[2])
                        newBal = prevBal+win
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                        await message.channel.send("You win \n"+str(win)+" "+currency+" has been added to your bank")
                    elif rps2 == 3:
                        await message.channel.send("You lose \n"+content[2]+" "+currency+' has been withdrawn from your bank')
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        newBal = prevBal-int(content[2])
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                elif rps == 3:
                    if rps2 == 2:
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        if prevBal >= 10000000:
                            win = int(int(content[2])/(prevBal/10000000))
                        else:
                            win = int(content[2])
                        newBal = prevBal+win
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                        await message.channel.send("You win \n"+str(win)+" "+currency+" has been added to your bank")
                    elif rps2 == 1:
                        await message.channel.send("You lose \n"+content[2]+" "+currency+' has been withdrawn from your bank')
                        prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        newBal = prevBal-int(content[2])
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                else:
                    #Again, should hopefully never be called, but just in case
                    await message.channel.send("I'm sorry, but something has gone very wrong. \nThe dev has been notified")
                    print ('Fatal error in guild: '+str(message.guild.id)+'\nBot: '+botName+' ('+str(client.user)+'\nrps command tree 2')
        
        #roulette command tree
        elif message.content.startswith(prefix+'roulette') or message.content.startswith(prefix+'r'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You don't have a bank for me to get the money out of, or put your non-winnings into \n`"+prefix+"setup`")
            elif message.content[len(prefix)+3:] == '':
                await message.channel.send("Incorrect command usage")
            else:
                if content[1] == "start":
                    if gambleDB.find_one({"action": "roulette", "guild": message.guild.id}) == None:
                        await message.channel.send("A Roulette game has been started. Do `"+prefix+"r add` to bet some "+currency+"\nThe wheel will be spun in 5 minuets")
                        ID = random.randint(1000000000000000,9999999999999999)
                        workDB.insert_one({"timeLeft": 300, "action": "roulette", "id": ID, "guild": message.guild.id})
                        gambleDB.insert_one({"action": "roulette", "id": ID, "guild": message.guild.id, "channel": message.channel.id})
                        await asyncio.sleep(300)
                        num = random.randint(0,38)
                        var1 = True
                        await message.channel.send("The wheel has been spun! \nAll the people who entered have been DM'd how much they won or lost")
                        wins = 0
                        losses = 0
                        while var1:
                            if gambleDB.find_one({"id": ID, "action": "rouletteBet"}) == None:
                                var1 == False
                                gambleDB.find_one_and_delete({"id": ID, "action":"roulette"})
                                await message.channel.send("There were "+str(wins)+" winners and "+str(losses)+" losers")
                                return
                            else:
                                author = gambleDB.find_one({"id":ID, "action": "rouletteBet"})["author"]
                                user = client.get_user(author)
                                betType = gambleDB.find_one({"author":author,"id":ID})["bet"]
                                bet = gambleDB.find_one({"author":author,"id":ID, "bet": betType})["amount"]
                                if betType == "row":
                                    if num == 0 or num == 37:
                                        wins+=1
                                        winnings = bet*17
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "split":
                                    num1 = gambleDB.find_one({"author":author,"id":ID, "bet": betType})["number1"]
                                    num2 = gambleDB.find_one({"author":author,"id":ID, "bet": betType})["number2"]
                                    if num == num1 or num == num2:
                                        wins+=1
                                        winnings = bet*17
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "street":
                                    street = gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})["number"]
                                    num1 = 0 #0 is lose, 1 is win
                                    num2 = 1
                                    while num2 <= 34:
                                        if num in [num2,num2+1,num2+2]:
                                            num1 = 1
                                        num2 += 3
                                    if num1 == 1:
                                        wins+=1
                                        winnings = bet*11
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "corner":
                                    if num in gambleDB.find_one({"author":author,"id":ID, "bet": betType})["numbers"]:
                                        wins+=1
                                        winnings = bet*8
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "basket":
                                    if num in [0,1,2,37]:
                                        wins+=1
                                        winnings = bet*6
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "double":
                                    street = gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})["number"]
                                    num1 = 0 #0 is lose, 1 is win
                                    num2 = 1
                                    while num2 <= 34:
                                        if num in [num2,num2+1,num2+2,num2+3,num2+4,num2+5]:
                                            num1 = 1
                                        num2 += 3
                                    if num1 == 1:
                                        wins+=1
                                        winnings = bet*5
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "column":
                                    column = gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})["number"]
                                    num1 = 0 #0 is lose, 1 is win
                                    if column == 1:
                                        if num in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]:
                                            num1 == 1
                                    elif column == 2:
                                        if num in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]:
                                            num1 == 1
                                    elif column == 3:
                                        if num in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]:
                                            num1 == 1
                                    if num1 == 1:
                                        wins+=1
                                        winnings = bet*2
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "dozen":
                                    dozen = gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})["number"]
                                    num1 = 0 #0 is lose, 1 is win
                                    if dozen == 1:
                                        if num in [1,2,3,4,5,6,7,8,9,10,11,12]:
                                            num1 == 1
                                    elif dozen == 2:
                                        if num in [13,14,15,16,17,18,19,20,21,22,23,24]:
                                            num1 == 1
                                    elif dozen == 3:
                                        if num in [25,26,27,28,29,30,31,32,33,34,35,36]:
                                            num1 == 1
                                    if num1 == 1:
                                        wins+=1
                                        winnings = bet*2
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "odd":
                                    if num in [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35]:
                                        wins+=1
                                        winnings = bet
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "even":
                                    if num in [2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36]:
                                        wins+=1
                                        winnings = bet
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "red":
                                    if num in [32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3]:
                                        wins+=1
                                        winnings = bet
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "black":
                                    if num in [15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26]:
                                        wins+=1
                                        winnings = bet
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                elif betType == "half":
                                    num1 = 0 #you get the idea
                                    half = gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})["number"]
                                    if half == 1:
                                        if num in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]:
                                            num1 = 1
                                    elif half == 2:
                                        if num in [19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]:
                                            num1 = 1
                                    if num1 == 1:
                                        wins+=1
                                        winnings = bet
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                else:
                                    if num == 37: num == "00"
                                    if str(num) == betType:
                                        wins+=1
                                        winnings = bet*35
                                        bal = currencyDB.find_one({"userID": author})["birbSeed"]
                                        currencyDB.find_one_and_update({"userID": author},{"$set":{"birbSeed": int(bal+winnings)}})
                                        await user.send("You won the roulette! "+str(winnings)+" birbseed has been added to your bank. \nYou now have "+str(bal+winnings)+" birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                    else:
                        timeLeft = workDB.find_one({"action": "roulette", "guild": message.guild.id})["timeLeft"]
                        await message.channel.send("A Roulette game is already in progress in this server. Do `"+prefix+"add` to bet some "+currency+"\n There is "+str(timeLeft)+" seconds left in this game")
                elif content[1] == "add":
                    if message.content[len(content[0])+len(content[1])+1:] == '':
                        await message.channel.send("Command usage: `add {bet} {location}`")
                    elif message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                        await message.channel.send("Command usage: `add {bet} {location}`")
                    elif content[2] == '' or content[2].isdecimal() == False:
                        await message.channel.send("Please provide an ammount to gamble with")
                    elif int(content[2]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                        await message.channel.send("You have insufficient funds for the operation")
                    elif int(content[2]) == 0:
                        await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
                    elif gambleDB.find_one({"action": "roulette", "guild": message.guild.id}) == None:
                        await message.channel.send("There is no active roulette game for this guild. \nDo `"+prefix+"roulette start`")
                    else:
                        if content[3] == "row":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "split":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+1:] == "":
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                return
                            elif content[5].isdecimal() == False or content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                return
                            if int(content[4]) in [1,4,7,10,13,16,19,22,25,28,31,34]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) - 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    return
                            elif int(content[4]) in [2,5,8,11,14,17,20,23,26,29,32,35]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) - 1 != int(content[4]) and int(content[5]) + 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    return
                            elif int(content[4]) in [3,6,9,12,15,18,21,24,27,30,33,36]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) + 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    return
                            else:
                                await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                return                                
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = int(content[2])
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id,"number1": int(content[4]), "number2": int(content[5])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "street":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+1:] == "":
                                await message.channel.send("Command usage = `street {first number of street}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `street {first number of street}`")
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `street {first number of street}`")
                                return
                            num = 0
                            num2 = 1
                            num3 = 0
                            while num2 <= 34:
                                if content[4] == str(num2): num = int(content[4])
                                else: num3 += 1
                                num2 += 3
                            if num3 == 12:
                                await message.channel.send("Street numbers: 1,4,7,10,13,16,19,22,25,28,31,34")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "corner":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+4:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+len(content[5])+5:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+len(content[5])+len(content[6])+6:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            arr = [int(content[4]), int(content[5]), int(content[6]), int(content[7])]
                            if arr not in [[1,2,4,5],[2,3,5,6],[4,5,7,8],[5,6,8,9],[7,8,10,11],[8,9,11,12],[10,11,13,14],[11,12,14,15],[16,17,19,20],[17,18,20,21],[19,20,22,23],[20,21,23,24],[22,23,25,26],[23,24,26,27],[25,26,28,29],[26,27,29,30],[28,29,31,32],[29,30,32,33],[31,32,34,35],[32,33,35,36]]:
                                await message.channel.send("A corner needs to be four numbers in a square, (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg) \nI.e. 1 2 4 5 or 22 23 25 26 \n*if all 4 numbers are in a square, make sure theyre in ascending order (lo-hi)*")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "numbers": arr})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "basket":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "double":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+1:] == "":
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                return
                            elif content[5].isdecimal() == False:
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                return
                            num = 0
                            num2 = 1
                            num3 = 0
                            while num2 <= 31:
                                if int(content[5]) == num2: num = int(content[5])
                                else: num3 += 1
                                num2 += 3
                            if num3 == 11:
                                await message.channel.send("Double street numbers: 1,4,7,10,13,16,19,22,25,28,31")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[5])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "column":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2 and int(content[4]) != 3:
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "dozen":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2 and int(content[4]) != 3:
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "odd":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "even":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "red":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "black":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "half":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2:
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        else:
                            if message.content[len(content[0])+len(content[1])+1:] == "":
                                await message.channel.send("Please input a valid bet name")
                                return
                            elif content[2].isdecimal() == False:
                                await message.channel.send("Please input a valid bet name")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+1:] == "":
                                await message.channel.send("Please input a valid amount")
                                return
                            elif content[3].isdecimal() == False:
                                await message.channel.send("Please input a valid amount")
                                return
                            for i in range(0,38):
                                if i == 37:
                                    i = "00"
                                if content[3] == str(i):
                                    ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                                    bet = content[2]
                                    oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                    newBal = oldBal-int(bet)
                                    currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                                    timeLeft = workDB.find_one({"id": ID})["timeLeft"]
                                    gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                                    await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")

        #blackjack command tree
        elif message.content.startswith(prefix+'blackjack'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You don't have a bank for me to get the money out of, or put your non-winnings into \n`"+prefix+"setup`")
            elif message.content[len(prefix)+3:] == '':
                await message.channel.send("Incorrect command usage")
            elif content[2] == '' or content[2].isdecimal() == False:
                await message.channel.send("Please provide an ammount to gamble with")
            elif int(content[2]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                await message.channel.send("You have insufficient funds for the operation")
            elif int(content[2]) == 0:
                await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
            else:
                #Finish this later as well
                return
            
        #slot machine command tree
        elif message.content.startswith(prefix+'slotmachine') or message.content.startswith(prefix+'smachine') or message.content.startswith(prefix+'sm'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You don't have a bank for me to get the money out of, or put your non-winnings into \n`"+prefix+"setup`")
            elif message.content[len(prefix)+3:] == '':
                await message.channel.send("Incorrect command usage")
            elif content[2] == '' or content[2].isdecimal() == False:
                await message.channel.send("Please provide an ammount to gamble with")
            elif int(content[2]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                await message.channel.send("You have insufficient funds for the operation")
            elif int(content[2]) == 0:
                await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
            else:
                #Add emojis for the different machine icons in TestServer and program the bot to use them
                return
            
        #highlow command tree
        elif message.content.startswith(prefix+'highlow') or message.content.startswith(prefix+'hl') or message.content.startswith(prefix+'hilo'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You don't have a bank for me to get the money out of, or put your non-winnings into \n`"+prefix+"setup`")
            elif message.content[len(content[0]):] == '' or content[1].isdecimal() == False:
                await message.channel.send("Please provide an ammount to gamble with")
            elif int(content[1]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                await message.channel.send("You have insufficient funds for the operation")
            elif int(content[1]) == 0:
                await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
            else:
                num = random.randint(1,100)
                num2 = random.randint(1,100)
                if num > num2:
                    num3 = 1
                elif num < num2:
                    num3 = 2
                elif num == num2:
                    num3 = 3
                else:
                    num3 = 3
                await message.channel.send("Do you think that "+str(num)+" is higher or lower than the number?")
                workDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "hilo",
                                   "timeLeft": 10,
                                   "bot": client.user.id,
                                   "result": num3,
                                   "number": num2,
                                   "bet": content[1]})
        elif workDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "hilo"}) != None:
            content = message.content.split()
            guess1 = content[0].lower()
            result = workDB.find_one({"userID": message.author.id, "action": "hilo"})["result"]
            number = workDB.find_one({"userID": message.author.id, "action": "hilo"})["number"]
            bet = workDB.find_one({"userID": message.author.id, "action": "hilo"})["bet"]
            if guess1 == 'hi' or guess1 == 'high' or guess1 == 'h' or guess1 == 'higher':
                guess = 1
            elif guess1 == 'lo' or guess1 == 'low' or guess1 == 'l' or guess1 == 'lower':
                guess = 2
            else:
                await message.channel.send("Incorrect command usage")
                workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                guess = 3
                return
            #Result 1:hi 2:lo 3:draw/err   Guess 1:hi 2:lo 3:err
            if result == 1:
                if guess == 1:
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    if prevBal >= 10000000:
                        win = int(int(bet)/(prevBal/10000000))
                    else:
                        win = int(bet)
                    newBal = prevBal+win
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    await message.channel.send("You win. The number was higher. \n"+str(win)+" "+currency+" has been added to your bank \nThe number was "+str(number))
                    workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 2:
                    await message.channel.send("You lose. The number was higher. \n"+str(bet)+" "+currency+" has been withdrawn from your bank \nThe number was "+str(number))
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    newBal = prevBal-int(bet)
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 3:
                    return
            elif result == 2:
                if guess == 1:
                    await message.channel.send("You lose. The number was lower. \n"+str(bet)+" "+currency+" has been withdrawn from your bank \nThe number was "+str(number))
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    newBal = prevBal-int(bet)
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 2:
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    if prevBal >= 10000000:
                        win = int(int(bet)/(prevBal/10000000))
                    else:
                        win = int(bet)
                    newBal = prevBal+win
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    await message.channel.send("You win. The number was lower. \n"+str(win)+" "+currency+" has been added to your bank \nThe number was "+str(number))
                    workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 3:
                    return
            elif result == 3:
                await message.content.send("The numbers were the same. Your bank ballance will also stay the same")
                workDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})            
            
        #invite command tree
        elif message.content.startswith(prefix+'invite'):
            await message.channel.send("Invite link for me: \nhttps://discord.com/api/oauth2/authorize?client_id=730483800626167818&permissions=8&scope=bot")
            
        #rob command tree
        elif message.content.startswith(prefix+'rob') or message.content.startswith(prefix+'bankrob'):
            content = message.content.split()
            if currencyDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("You have no bank to put your *winnings* in \n`"+prefix+"setup`")
            elif (message.content[len(content[0]):] == '') or (message.mentions == 0 or None):
                await message.channel.send("Incorrect command usage")
            elif currencyDB.find_one({"userID": message.mentions[0].id}) == None:
                await message.channel.send("Your ~~fri~~enemy has no bank that you can steal out of. I ain't letting you steal their possesions \nTough luck")
            elif message.mentions[0].id == message.author.id:
                await message.channel.send("You cannot rob yourself.")
            else:
                maximum = 0
                caught = False
                pingID = message.mentions[0].id
                num = random.randint(1,10)
                if num == 1 or num == 2 or num == 3 or num == 10:
                    maximum = (currencyDB.find_one({"userID": pingID})["birbSeed"])/4
                    caught = False
                elif num == 4 or num == 5 or num == 6 or num == 7 or num == 8:
                    maximum = (currencyDB.find_one({"userID": message.author.id})["birbSeed"])/4
                    caught = True
                elif num == 9:
                    maximum = (currencyDB.find_one({"userID": pingID})["birbSeed"])/2
                    caught = False 
                else:
                    return
                if caught == True:
                    num2 = random.randint(1, int(maximum))
                    await message.channel.send("You were caught red handed! \nBecause of this, you have been forced to pay "+str(num2)+" "+currency+" to the person you tried to rob \nTough luck ~~serves you right~~")
                    newBal = currencyDB.find_one({"userID": pingID})["birbSeed"]+num2
                    newBal2 = currencyDB.find_one({"userID": message.author.id})["birbSeed"]-num2
                    currencyDB.find_one_and_update({"userID": pingID}, {"$set":{"birbSeed": newBal}})
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal2}})
                else:
                    num2 = random.randint(1, int(maximum))
                    await message.channel.send("You succeeded! \nYou managed to steal "+str(num2)+" "+currency+" from the person \nCongrats ~~I knew you could do it~~")
                    newBal = currencyDB.find_one({"userID": pingID})["birbSeed"]-num2
                    newBal2 = currencyDB.find_one({"userID": message.author.id})["birbSeed"]+num2
                    currencyDB.find_one_and_update({"userID": pingID}, {"$set":{"birbSeed": newBal}})
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal2}})

        #ping command tree
        elif message.content.startswith(prefix+'ping'):
            await message.channel.send("pong")
            latency = client.latency    
            await message.channel.send("Latency: "+str(latency)[2:5]+"ms")

        #setmessage command tree
        elif message.content.startswith(prefix+'setmessage'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if message.content[len(prefix)+10:] == '':
                    await message.channel.send("Incorrect command usage")
                elif content[1] == "join":
                    await message.channel.send("What would you like to set this servers join message to? (typing {user} pings the user) \nThis has an automatic 1m timeout")
                    workDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "setMessage",
                                       "timeLeft": 60,
                                       "bot": client.user.id,
                                       "action2": "join"})
                elif content[1] == "leave":
                    await message.channel.send("What would you like to set this servers leave message to? (typing {user} pings the user) \nThis has an automatic 1m timeout")
                    workDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "setMessage",
                                       "timeLeft": 60,
                                       "bot": client.user.id,
                                       "action2": "leave"})
                else:
                    await message.channel.send("Please input a valid subcommand")
        elif workDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "setMessage"}) != None:
            action = workDB.find_one({"userID": message.author.id, "action": "setMessage"})["action2"]
            if action == "join":
                serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"joinMessage": message.content}})
                await message.channel.send("The join message has been updated :thumbsup:")
                workDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})
            elif action == "leave":
                serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"leaveMessage": message.content}})
                await message.channel.send("The leave message has been updated :thumbsup:")
                workDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})
            else:
                workDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})

        #welcometest command tree
        elif message.content.startswith(prefix+"welcometest"):
            if serverDB.find_one({"serverID": message.guild.id}) == None:
                return
            elif serverDB.find_one({"serverID": message.guild.id})["joinMessage"] == "":
                return
            elif serverDB.find_one({"serverID": message.guild.id})["joinMessage"] == None:
                return
            else:
                message1 = serverDB.find_one({"serverID": message.guild.id})["joinMessage"]
                await message.channel.send(message1.replace("{user}", "<@"+str(message.author.id)+">"))

        #leavetest command tree
        elif message.content.startswith(prefix+"leavetest"):
            if serverDB.find_one({"serverID": message.guild.id}) == None:
                return
            elif serverDB.find_one({"serverID": message.guild.id})["leaveMessage"] == "":
                return
            elif serverDB.find_one({"serverID": message.guild.id})["leaveMessage"] == None:
                return
            else:
                message1 = serverDB.find_one({"serverID": message.guild.id})["leaveMessage"]
                await message.channel.send(message1.replace("{user}", "<@"+str(message.author.id)+">"))

        #kick command tree
        elif message.content.startswith(prefix+"kick"):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if message.content[len(prefix)+5:] == '':
                    await message.channel.send("Memebr not found")
                elif message.mentions == None:
                    await message.channel.send("Member not found")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to kick that user")
                else:
                    await message.guild.kick(message.mentions[0],reason="ROBIRB KICK COMMAND")
                    await message.channel.send("Successfully kicked <@"+str(message.mentions[0].id)+"> :thumbsup:")

        #ban command tree
        elif message.content.startswith(prefix+"ban"):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if message.content[len(prefix)+4:] == '':
                    await message.channel.send("Memebr not found")
                elif message.mentions == None:
                    await message.channel.send("Member not found")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to ban that user")
                else:
                    num = 0
                    if message.content[len(prefix)+len(content[0])+len(content[1]):] == '':
                        num = 0
                    else:
                        num = int(content[2])
                    await message.guild.ban(message.mentions[0],reason="ROBIRB BAN COMMAND",delete_message_days=num)
                    await message.channel.send("Successfully banned <@"+str(message.mentions[0].id)+"> :thumbsup:")

        elif message.content.startswith(prefix+"unban"):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if message.content[len(prefix)+6:] == '':
                    await message.channel.send("Member not found")
                elif message.mentions == None:
                    await message.channel.send("Member not found")
                else:
                    await message.guild.unban(message.mentions[0],reason="ROBIRB UNBAN COMMAND",)

        #mute command tree
        elif message.content.startswith(prefix+"mute"):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send("There is no database setup for this server. \nPlease run `"+prefix+"serversetup`")
                elif message.content[len(prefix)+5:] == '':
                    await message.channel.send("Member not found")
                elif message.mentions == None:
                    await message.channel.send("Member not found")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to mute that user")
                else:
                    muteRole = ''
                    if serverDB.find_one({"serverID": message.guild.id})['muteRole'] == None or serverDB.find_one({"serverID": message.guild.id})['muteRole'] == '':
                        await message.guild.create_role(name="Muted", reason="ROBIRB COMMAND")
                        roles = message.guild.roles
                        serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"muteRole": roles[1].id}})
                        channels = message.guild.text_channels
                        for i in range(0,len(channels)):
                            await channels[i].set_permissions(roles[1], send_messages=False)
                        await message.guild.edit_role_positions({roles[1]:(client.top_role.position-1)})
                        muteRole = roles[1]
                    else:
                        muteRole = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["muteRole"])
                    await message.mentions[0].add_roles(message.guild.get_role(int(serverDB.find_one({"serverID": message.guild.id})["muteRole"]))  , reason="USER MUTED")
                    await message.channel.send("Successfully muted <@"+str(message.mentions[0].id)+"> :thumbsup:")
                    
        #unmute command tree
        elif message.content.startswith(prefix+'unmute'):
            content = message.content.split()
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('There is no database setup for this server. \nPlease run `'+prefix+'serversetup`')
                elif message.content[len(prefix)+5:] == '':
                    await message.channel.send('Member not found')
                elif message.mentions == None:
                    await message.channel.send('Member not found')
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to unmute that user")
                else:
                    muteRole = ''
                    if serverDB.find_one({"serverID": message.guild.id})["muteRole"] == '':
                        await message.channel.send("I have not muted anybody in this server")
                    else:
                        muteRole = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["muteRole"])
                        await message.mentions[0].remove_roles(muteRole, reason="USER UNMUTED")
                        await message.channel.send("Successfully unmuted <@"+str(message.mentions[0].id)+"> :thumbsup:")
                                             
        #inventory command tree
        elif message.content.startswith(prefix+'inventory') or message.content.startswith(prefix+'inv'):
            if invDB.find_one({"userID": message.author.id}) == None:
                await message.channel.send("Your inventory is empty")
            elif invDB.find_one({"userID": message.author.id})["items"] == 0:
                await message.channel.send("Your inventory is empty")
            else:
                #num = {}
                embed = discord.Embed(title = "__Your Inventory__", colour = 0xFA00FF)
                for i in range(1,13):
                    if invDB.find_one({"userID": message.author.id})[str(i)] != 0:
                        #num[i] = invDB.find_one({"userID": message.content.id})[i]
                        embed.add_field(name=invDB.find_one({"list": "name"})[str(i)], value = invDB.find_one({"userID": message.author.id})[str(i)])
                await message.channel.send(embed=embed)

        #settings command tree
        elif message.content.startswith(prefix+'settings'):
            return #Finish later
            #I can't even remember what I wanted a settings command for :think:
        
        #merchant command tree
        elif message.content.startswith(prefix+'merchant') or message.content.startswith(prefix+'m'):
            content = message.content.split()
            if workDB.find_one({"userID": "rb.Merchant"}) != None:
                timeLeft = workDB.find_one({"userID": "rb.Merchant"})["timeLeft"]
                seconds = timeLeft % (24 * 3600)
                hour = seconds // 3600
                seconds = seconds % 3600
                minutes = seconds // 60
                seconds = seconds % 60
                await message.channel.send("There is no merchant right now. Try looking again in "+str(hour)+':'+str(minutes)+':'+str(seconds))
            else:
                if currencyDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("\"I can't go around talking to people who don't even have a bank that I can take from!\"\n(Do `"+prefix+"setup`!)")
                elif invDB.find_one({"userID":message.author.id}) == None:
                    await message.channel.send("\"I can't go around talking to people who don't even have an inventory that I can take from!\"\n(Do `"+prefix+"setup`!)")
                else:
                    #THE NUMBER: values 1 through 23 are for buying, numbers 24 through 46 are for selling
                    #Any given number can be from 1 to 8. If the value is 3,4,5 or 6, the item will not show up (buying)
                    #If no items are shown, then pick a random number between 1 and 23 and show the corrisponding item
                    #If the value is 1 or 2, make the item cheaper than the shop (1 cheaper than 2)
                    #if the value is 7 or 8, make the item more expensive than the shop (7 cheaper than 8)
                    #With selling, for each value, pick a random number between (num/10) and 1.  (item selling cost = half the item cost)
                    #If the original number is between 1 and 4, divide the item selling cost by the random number
                    #If the original number is betweem 5 and 8, multiply the item selling cost by the random number
                    #This is going to take fucking forever
                    if message.content[len(prefix)+len(content[0]):] == '':
                        await message.channel.send("\"What can I do for ya, kid?\"\n(`"+prefix+"m buy`,`"+prefix+"m sell`)")
                    elif content[1] == 'buy':
                        if message.content[len(prefix)+len(content[0])+len(content[1]):] == '':
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                        elif content[2] == 'inventory' or content[2] == 'inv':
                            num2 = 0
                            embed = discord.Embed(title = "__Merchants Shop__", description="Do `"+prefix+"shop item {number}` to find out about the item", colour = 0x8F00FF)
                            for i in range(1,12):
                                num = currencyDB.find_one({"userID": "rb.Merchant"})[str(i)]
                                if num == 3 or num == 4 or num == 5 or num == 6:
                                    num2 += 1
                                    continue
                                else:
                                    price = float(invDB.find_one({"list":"price"})[str(i)])
                                    if num == 1:
                                        price = int(price*0.75)
                                    elif num == 2:
                                        price = int(price*0.85)
                                    elif num == 7:
                                        price = int(price*1.15)
                                    elif num == 8:
                                        price = int(price*1.25)
                                    embed.add_field(name=str(i)+': '+invDB.find_one({"list":"name"})[str(i)], value= str(price))
                            if num2 == 12:
                                num3 = random.randint(1,12)
                                num = currencyDB.find_one({"userID":"rb.Merchant"})[str(num3)]
                                price = float(invDB.find_one({"list": "price"})[str(num3)])
                                if num == 1:
                                    price = int(price*0.75)
                                elif num == 2:
                                    price = int(price*0.85)
                                elif num == 7:
                                    price = int(price*1.15)
                                elif num == 8:
                                    price = int(price*1.25)
                                    embed.add_field(name=str(num3)+': '+invDB.find_one({"list":"name"}[str(num3)], value=str(price)))
                            embed.set_footer(text="Page 1")
                            await message.channel.send(embed=embed)
                        elif content[2] == 'item':
                            if message.content[len(content[0])+9:] == '':
                                await message.channel.send("Please provide a valid item number to buy")
                                return
                            for a in range(1,12):
                                num = currencyDB.find_one({"userID":"rb.Merchant"})[str(a)]
                                if str(a) == content[3]:
                                    if num == 3 or num == 4 or num == 5 or num == 6:
                                        await message.channel.send("\"I ain't selling that, kid!\"")
                                        continue
                                    if message.content[len(prefix)+len(content[0])+len(content[1])+len(content[2])+len(content[3])+2:] == '':
                                        c = 1
                                    elif content[4].isdecimal == True:
                                        c = int(content[4])
                                    else:
                                        c = int(content[4])
                                    if str(a) == "6":
                                        i = 5
                                        b = (3*c)
                                    else:
                                        i = a
                                        b = c
                                    bankBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                    price = float(invDB.find_one({"list":"price"})[str(i)])
                                    if num == 1:
                                        price = int(price*0.75)
                                    elif num == 2:
                                        price = int(price*0.85)
                                    elif num == 7:
                                        price = int(price*1.15)
                                    elif num == 8:
                                        price = int(price*1.25)
                                    if int(bankBal) < int(int(price)*c):
                                        await message.channel.send("You can't afford that.")
                                    else:
                                        newBal = int(bankBal) - int(int(price)*c)
                                        if invDB.find_one({"userID": message.author.id}) == None:
                                            invDB.insert_one({"userID": message.author.id, "items": 0})
                                            for a in range(1,24):
                                                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(a): 0}})
                                        items = invDB.find_one({"userID": message.author.id})["items"]
                                        if invDB.find_one({"userID": message.author.id})[str(i)] == None:
                                            invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(i): int(b)}})
                                            invDB.find_one_and_update({"userID": message.author.id}, {"$set":{"items": int(items)+int(b)}})
                                        else:
                                            num = invDB.find_one({"userID": message.author.id})[str(i)]
                                            invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(i): (int(num)+int(b))}})
                                            invDB.find_one_and_update({"userID": message.author.id}, {"$set":{"items": int(items)+int(b)}})
                                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                                        name = invDB.find_one({"list": "name"})[str(a)]
                                        await message.channel.send("You just bought "+str(c)+" "+name.lower()+"! You now have "+str(newBal)+" "+currency)
                        else:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                    elif content[1] == 'sell':
                        if message.content[len(prefix)+len(content[0])+len(content[1]):] == '':
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                        elif content[2] == 'inventory' or content[2] == 'inv':
                            embed = discord.Embed(title = "__Merchants Request List__", description="Basically, this is what he wants to buy, and how much he'll pay per item", colour = 0x39FF14)
                            for i in range(24,35):
                                num = currencyDB.find_one({"userID": "rb.Merchant"})[str(i-23)]
                                num2 = currencyDB.find_one({"userID": "rb.Merchant"})[str(i)]
                                price = (int(invDB.find_one({"list":"price"})[str(i-23)])/2)
                                if num <= 4:
                                    price = price/num2
                                else: price = price*num2
                                embed.add_field(name=str(i-23)+': '+invDB.find_one({"list":"name"})[str(i-23)], value=str(int(price)))
                            embed.set_footer(text="Page 1")
                            await message.channel.send(embed=embed)
                        elif content[2] == 'item':
                            if message.content[len(prefix)+10:] == '':
                                await message.channel.send("Please provide an item number to sell")
                            else:
                                for i in range(1,24):
                                    if content[3] == str(i):
                                        if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                            await message.channel.send("You don't own any of this item. In which case, you cannot sell it")
                                        else:
                                            #await message.channel.send(message.content[(len(prefix)+len(str(content[2]))+10):])
                                            if message.content[len(prefix)+len(content[0])+len(content[1])+len(content[2])+len(content[3])+2:] == "":
                                                num = 87982388927
                                            elif content[4].isdecimal() == True:
                                                num = int(content[4])
                                            else: num = 1
                                            amount = invDB.find_one({"userID": message.author.id})[str(content[3])]
                                            if amount < num:
                                                await message.channel.send("You don't have the required amount of items. And you cannot sell air")
                                            else:
                                                num2 = currencyDB.find_one({"userID":"rb.Merchant"})[str(i)]
                                                num3 = currencyDB.find_one({"userID": "rb.Merchant"})[str(i+23)]
                                                price = (int(invDB.find_one({"list": "price"})[str(content[3])])/2)
                                                if num2 <= 4:
                                                    price = int(price/num3)*int(num)
                                                else: price = int(price*num3)*int(num)
                                                invDB.find_one_and_update({"userID": message.author.id},{"$set":{str(content[3]):(amount-num)}})
                                                prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                                currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": (prevBal+price)}})
                                                name = invDB.find_one({"list": "name"})[str(content[3])]
                                                await message.channel.send("You have successfully sold "+str(num)+" "+name+"!\nYou have earned "+str(price)+" "+currency)
                        else:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                
        elif christmas == True:
            #------------------
            #Christmas Commands
            #------------------
    
            #christmasify command tree
            if message.content.startswith(prefix+"christmasify"):
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmasDB.insert_one({"userID": message.author.id, "snowBalls": 0, "hits": 0, "timesHit": 0, "misses":0})
                    await message.channel.send("You are even more christmassy now!")
                else:
                    await message.channel.send("You're already as christmassy as can be!")
    
            #collect command tree
            elif message.content.startswith(prefix+'collect'):
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("Quick, do `"+prefix+"christmasify`!")
                elif workDB.find_one({"userID":message.author.id, "action":"ballCollect"}) != None:
                    timeLeft = workDB.find_one({"userID": message.author.id, "action":"ballCollect"})["timeLeft"]
                    minutes = timeLeft // 60
                    seconds = timeLeft % 60
                    await message.channel.send("Your hands are still cold from last time! Come back in "+str(minutes)+':'+str(seconds)+" to get more!")
                else:
                    num = random.randint(5, 50)
                    balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                    balls = balls + num
                    christmasDB.find_one_and_update({"userID":message.author.id}, {"$set":{"snowBalls": balls}})
                    await message.channel.send("You have collected "+str(num)+" snowballs. You now have "+str(balls)+" snowballs. \nUse `"+prefix+"throw` to throw a snowball at a friend!")
                    workDB.insert_one({"userID": message.author.id, "action": "ballCollect", "timeLeft": 300})

            #throw command tree
            elif message.content.startswith(prefix+"throw"):
                content = message.content.split()
                if message.content[6+len(prefix):] == '':
                    await message.channel.send("You can't throw a snowball at nobody!")
                elif christmasDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("You don't have any snowballs to throw! \n(Do `"+prefix+"christmasify`, then `"+prefix+"collect`)")
                elif christmasDB.find_one({"userID": message.author.id})["snowBalls"] == 0:
                    await message.channel.send("You dont have any snow balls to throw! \n(Do `"+prefix+"collect`)")
                else:
                    num = random.randint(0,1)
                    if num == 0:
                        balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                        balls = balls-1
                        misses = christmasDB.find_one({"userID": message.author.id})["misses"]
                        misses = misses+1
                        christmasDB.find_one_and_update({"userID": message.author.id}, {"$set":{"snowballs": balls, "misses": misses}})
                        await message.channel.send("You missed them. \nCongratulations!")
                    else:
                        if christmasDB.find_one({"userID": message.mentions[0].id}) == None:
                            christmasDB.insert_one({"userID": message.mentions[0].id, "snowBalls": 0, "hits": 0, "timesHit": 0, "misses": 0})
                        timesHit = christmasDB.find_one({"userID": message.mentions[0].id})["timesHit"]
                        timesHit = timesHit+1
                        balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                        balls = balls-1
                        hits = christmasDB.find_one({"userID": message.author.id})["hits"]
                        hits = hits+1
                        christmasDB.find_one_and_update({"userID": message.mentions[0].id}, {"$set":{"timesHit": timesHit}})
                        christmasDB.find_one_and_update({"userID": message.author.id}, {"$set":{"balls": balls, "hits": hits}})
                        await message.channel.send("You wacked <@"+str(message.mentions[0].id)+"> with a snowball! \nOuch!")

            #stats command tree
            elif message.content.startswith(prefix+"stats"):
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("Quick, do `"+prefix+"christmasify`!")
                else:
                    content = message.content.split()
                    balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                    hits = christmasDB.find_one({"userID": message.author.id})["hits"]
                    timesHit = christmasDB.find_one({"userID": message.author.id})["timesHit"]
                    misses = christmasDB.find_one({"userID": message.author.id})["misses"]
                    await message.channel.send("__Your Christmas Stats__ \nSnowballs = "+str(balls)+"\nHits = "+str(hits)+"\nTimes Hit = "+str(timesHit)+"\nMisses = "+str(misses))
                
                

#Reports deleted messages
@client.event
async def on_message_delete(message):
    if serverDB.find_one({"serverID": message.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"] == "":
        return
    else:
        channel = message.guild.get_channel(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"]))))
        embed = discord.Embed(title = 'Message Deleted', colour = 0xFF0000)
        embed.set_author(name=message.author,  icon_url=message.author.avatar_url)
        embed.add_field(name='Deleted Message: ', value=message.content)
        embed.set_footer(text=message.guild.name+' - '+str(message.channel))
        await channel.send(embed=embed)

#Reports edited messages
@client.event
async def on_message_edit(message, message2):
    if serverDB.find_one({"serverID": message.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"] == "":
        return
    else:
        channel = message.guild.get_channel(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"]))))
        embed = discord.Embed(title = 'Message Edited', colour = 0xFF0000)
        embed.set_author(name=message.author,  icon_url=message.author.avatar_url)
        embed.add_field(name='Before: ', value=message.content, inline=True)
        embed.add_field(name='After: ', value=message2.content, inline=True)
        embed.set_footer(text=message.guild.name+' - '+str(message.channel))
        await channel.send(embed=embed)

#Called when the bot joins a server
@client.event
async def on_guild_join(guild):
    if serverDB.find_one({"serverID": guild.id}) == None:
        serverDB.insert_one({"serverID": guild.id,
                            "prefix": prefix,
                            "verificationRole": "",
                            "botSpamChannel": "",
                            "suggestionChannel": "",
                            "welcomeChannel": "",
                            "joinMessage": "",
                            "leaveMessage": "",
                            "muteChannel": ""})

#Called when the bot leaves a server
@client.event
async def on_guild_remove(guild):
    if serverDB.find_one({"serverID": guild.id}) != None:
        serverDB.find_one_and_delete({"serverID": guild.id})

#Called when a member joins a server
@client.event
async def on_member_join(member):
    if member.bot == True:
        return
    elif currencyDB.find_one({"userID": member.id}) == None and invDB.find_one({"userID": member.id}) == None:
        currencyDB.insert_one({"userID": member.id,
                                "levelXP": 0,
                                "birbSeed": 0,
                                "canDoDaily": 1,
                                "nextDaily": ""})
        invDB.insert_one({"userID": member.id, "items": 0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0})
    elif currencyDB.find_one({"userID": member.id}) != None and invDB.find_one({"userID": member.id}) == None:
        invDB.insert_one({"userID": member.id, "items": 0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0})
    elif currencyDB.find_one({"userID": member.id}) == None and invDB.find_one({"userID": member.id}) != None:
        currencyDB.insert_one({"userID": member.id,
                                "birbSeed": 0,
                                "canDoDaily": 1,
                                "nextDaily": ""})
    #Server specific join message
    if serverDB.find_one({"serverID": member.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": member.guild.id})["joinMessage"] == "":
        return
    elif serverDB.find_one({"serverID": member.guild.id})["joinMessage"] == None:
        return
    elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == "":
        return
    elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == None:
        return
    else:
        message = serverDB.find_one({"serverID": member.guild.id})["joinMessage"]
        channel = member.guild.get_channel(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"]))))
        await channel.send(message.replace("{user}", "<@"+str(member.id)+">"))


#Called when a member leaves a server
@client.event
async def on_member_remove(member):
    if member.bot == True:
        return
    else:
        #Server specific leave message
        if serverDB.find_one({"serverID": member.guild.id}) == None:
            return
        elif serverDB.find_one({"serverID": member.guild.id})["leaveMessage"] == "":
            return
        elif serverDB.find_one({"serverID": member.guild.id})["leaveMessage"] == None:
            return
        elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == "":
            return
        elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == None:
            return
        else:
            message = serverDB.find_one({"serverID": member.guild.id})["leaveMessage"]
            channel = member.guild.get_channel(int(''.join(filter(str.isdigit, serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"]))))
            await channel.send(message.replace("{user}", "<@"+str(member.id)+">"))



#Starup
client.run(token)
