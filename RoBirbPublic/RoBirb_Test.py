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
token = "Put your bots token here"
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f'{client.user} is online')
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Why hello there"))


#MongoDB Initialisation
mongoClient = MongoClient('Put your mongodb connection url here')
db = mongoClient.ThisIsYourBotsDatabase
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
            print (f'\nNew DM from: {message.author} ({message.author.id}) at: {datetime.datetime.now()}\nContent: {message.content}\nUploaded to directMessage database')
            if message.content in ["$restart", "$reboot", "$reset", "restart", "reboot", "reset"]:
                await message.channel.send("Nice try")
            elif "help" in message.content:
                await message.channel.send("If you want help on how to use me / what commands I have, go into a server that I am in and use the $help command! (custom prefixes do not matter with the help command)")
            else:
                await message.channel.send('Hippidy hoppidy you are now my property')
            dmDB.insert_one({"author": message.author.name,
                             "discriminator": message.author.discriminator,
                             "authorID": message.author.id,
                             "client": client.user.name,
                             "messageContent": message.content,
                             "time": datetime.datetime.now()})
            return
    elif isinstance(message.channel, discord.DMChannel) and message.author == client.user:
        return
    else:
        #All bot command trees. For real this time
        
        #Maks sure the bot doesn't respond to empty messages. Because those are things Discord sends for some reason
        if message.content == '': return
        
        #Makes content lowercase
        contentOriginal = message.content.split()
        content = []
        for i in range(0,len(contentOriginal)):
            content.append(contentOriginal[i].lower())
        
        #server specific prefix setup
        if serverDB.find_one({"serverID": message.guild.id}) == None:
            prefix = '$'
            currency = "money"
        else:
            prefix = serverDB.find_one({"serverID": message.guild.id})["prefix"]
            currency = serverDB.find_one({"serverID": message.guild.id})["currency"]

        def userSetup(userID):
            if currencyDB.find_one({"userID": userID}) == None and invDB.find_one({"userID": userID}) == None:
                currencyDB.insert_one({"userID": userID,
                                       "levelXP": 0,
                                       "birbSeed": 0,
                                       "accountID": "",
                                       "password": ""})
                doc = {"userID": userID, "items": 0}
                for i in range(1,110):
                    doc[str(i)] = 0
                invDB.insert_one(doc)
            elif currencyDB.find_one({"userID": userID}) != None and invDB.find_one({"userID": userID}) == None:
                doc = {"userID": userID, "items": 0}
                for i in range(1,110):
                    doc[str(i)] = 0
                invDB.insert_one(doc)
            elif currencyDB.find_one({"userID": userID}) == None and invDB.find_one({"userID": userID}) != None:
                currencyDB.insert_one({"userID": userID,
                                       "levelXP": 0,
                                       "birbSeed": 0,
                                       "accountID": "",
                                       "password": ""})
                
        def serverSetup(guildID):
            serverDB.insert_one({"serverID": message.guild.id,
                                "prefix": prefix,
                                "verificationRole": "",
                                "botSpamChannel": "",
                                "suggestionChannel": "",
                                "welcomeChannel": "",
                                "joinMessage": "",
                                "leaveMessage": "",
                                "muteRole": "",
                                "numColours": 0,
                                "botspamEnabled": False,
                                "welcomeEnabled": False,
                                "currency": "birbseed"})
            
        if content[0][0] == prefix and datetime.datetime.now().month == 9:
            if random.randint(1,20) == 6:
                num = random.randint(1,100)
                if num in range(1,50):
                    pumpkinType = 106
                    rarity = "common"
                elif num in range(51,78):
                    pumpkinType = 107
                    rarity = "uncommon"
                elif num in range(79,91):
                    pumpkinType = 108
                    rarity = "rare"
                elif num in range(92,97):
                    pumpkinType = 109
                    rarity = "epic"
                else:
                    pumpkinType = 110
                    rarity = "legendary"
                message1 = await message.author.send(f"You found a {rarity} Jack O' Lantern in {message.guild.name}!\nCheck your inventory (in any server that has me) to see how many you have!")
                if invDB.find_one({"userID": message.author.id}) == None:
                    userSetup(message.author.id)
                noPumpkins = (invDB.find_one({"userID": message.author.id})[str(pumpkinType)])+1
                invDB.find_one_and_update({"userID": message.author.id}, {"$set":{str(pumpkinType): noPumpkins}})
        
        #Makes sure the bot doesn't respond to its own messages
        if message.author == client.user:
            return
        
        #hello command tree
        elif content[0] == prefix+"hello":
            await message.channel.send('Hello!')

        #status command tree
        elif content[0] == prefix+'status':
            if message.author.id == ownerID:
                await client.change_presence(status=discord.Status.idle, activity=discord.Game(message.content[7+len(prefix):]))
                await message.delete()
            
        #dmme command tree
        elif content[0] == prefix+'dmme':
            await message.author.send("hi")
            
        #serversetup command tree
        elif content[0] == prefix+'serversetup':
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                    await message.channel.send('A record has been setup for this server in my database. The only data recorded is the server ID. You can add other data as well (custom prefix, verification role, bot spam channel). You can get your servers data with `serverdata`')
                else:
                    await message.channel.send('There are already records setup for this server.')

        #setrole command tree
        elif content[0] == prefix+'setrole':
            if message.author.guild_permissions.administrator:
                def helpText():
                    embed = discord.Embed(title="__**Set Role Help**__", description="**Admin only.** Do `"+prefix+"setrole {role (verification, for example)}` to set that role!", colour=0x32CD32)
                    embed.add_field(name="Verification", value=f"Sets the verification role. Find out more with `{prefix}help verification`")
                    embed.add_field(name="Mute", value=f"Sets the mute role. Find out more with `{prefix}help mute`")
                    embed.set_footer(text=f"Do `{prefix}help` to find out about what commands there are")
                    return embed
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if len(content) <= 1:
                    await message.channel.send(embed=helpText())
                elif content[1] == 'help':
                    await message.channel.send(embed=helpText())
                elif message.content[len(prefix)+8:] == '':
                    await message.channel.send("Please input a valid subcommand")
                else:
                    if 'verification' == content[1]: 
                        if message.content[len(prefix)+21:] == '':
                            await message.channel.send('Please input a role to set as the verification role')
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input a role to set as the verification role")
                        else:
                            ping = message.role_mentions[0].id
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"verificationRole": ping}})
                            await message.channel.send('The verification role of this server has been updated to: <@&'+str(serverDB.find_one({"serverID": message.guild.id})["verificationRole"])+">")
                    elif 'mute' == content[1]: 
                        if message.content[len(prefix)+21:] == '':
                            await message.channel.send('Please input a role to set as the mute role')
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input a role to set as the mute role")
                        else:
                            ping = message.role_mentions[0].id
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"muteRole": ping}})
                            await message.channel.send('The mute role of this server has been updated to: <@&'+str(serverDB.find_one({"serverID": message.guild.id})["muteRole"])+">")
                    else:
                        await message.channel.send(embed=helpText())
                    
        #setprefix command tree
        elif content[0] == prefix+'prefix' or content[0] == '$prefix' or content[0] == '$setprefix' or content[0] == prefix+'setprefix':
            if schedDB.find_one({"userID": message.author.id, "action": "prefixCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if len(content) == 1:
                await message.channel.send('The prefix for me in this server is '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"]))
            elif message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if content[1] == "reset":
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"prefix": "$"}})
                    await message.channel.send('The prefix for me in this server has now been reset to '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"]))
                elif len(content[1]) > 3:
                    await message.channel.send("Please send something to set as the prefix. \nMax of 3 characters.")
                else:
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"prefix": content[1]}})
                    await message.channel.send('The prefix for me in this server has now been updated to '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"]))
            else:
                await message.channel.send('The prefix for me in this server is '+str(serverDB.find_one({"serverID": message.guild.id})["prefix"]))
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"prefixCD"})
            
        #setcurrency command tree
        elif content[0] in [prefix+"currency", prefix+"setcurrency"]:
            if serverDB.find_one({"serverID": message.guild.id}) == None:
                serverSetup(message.guild.id)
            if not message.author.guild_permissions.administrator:
                return
            elif content[1] == "reset":
                serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"currency": "birbseed"}})
                await message.channel.send(f'The currency name for me in this server has now been reset from {currency} to {serverDB.find_one({"serverID": message.guild.id})["currency"]}')
            elif len(content[1]) > 10:
                await message.channel.send(f'The currency name cannot be longer than 10 characters')
            else:
                serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"currency": str(content[1])}})
                await message.channel.send(f'The currency name for me in this server has now been updated from \"{currency}\" to \"{serverDB.find_one({"serverID": message.guild.id})["currency"]}\"')

        #serverdata command tree
        elif content[0] == prefix+'serverdata':
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) != None:
                    doc = serverDB.find_one({"serverID": message.guild.id})
                    embed = discord.Embed(title="__Server Data__", description="The data that is recorded for this server on my database", colour=0x32CD32)
                    embed.add_field(name="EntryID (here for debugging)", value=doc["_id"])
                    embed.add_field(name="Botspam Channel", value=f'<#{doc["botSpamChannel"]}>')
                    embed.add_field(name="Botspam Enabled?", value=str(doc["botspamEnabled"]))
                    embed.add_field(name="Join Message", value=f'. {doc["LeaveMessage"]}', inline=False)
                    embed.add_field(name="Leave Message", value=f'. {doc["LeaveMessage"]}', inline=False)
                    embed.add_field(name="Currency", value=doc["currency"])
                    embed.add_field(name="Mute Role", value=f'<@{doc["muteRole"]}>')
                    embed.add_field(name="Number of Colours", value=str(doc["numColours"]))
                    embed.add_field(name="Prefix", value=doc["prefix"])
                    embed.add_field(name="ServerID", value=str(doc["serverID"]))
                    embed.add_field(name="Verification Role", value=f'<@{doc["verificationRole"]}>')
                    embed.add_field(name="Welcome Channel", value=f'<#{doc["welcomeChannel"]}>')
                    await message.channel.send('The data that is recorded for your server on my database:')
                    await message.channel.send(serverDB.find_one({"serverID": message.guild.id}))
                else:
                    await message.channel.send('No records found')

        #deleteserverdata command tree
        elif content[0] == prefix+'deleteserverdata':
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    await message.channel.send('No records found')
                else:
                    await message.channel.send('This action is irreversible. Do you wish to proceed? Y/N')
                    schedDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "deleteSData",
                                       "timeLeft": 10,
                                       "bot": client.user.id})
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "deleteSData"}) != None:
            if content[0] == 'y' or content == 'yes': 
                serverDB.find_one_and_delete({"serverID": message.guild.id})
                schedDB.find_one_and_delete({"userID": message.author.id})
                await message.channel.send('Operation sucessfull')
            else:
                await message.channle.send('Operation failure')
                           
        #verify command tree
        elif content[0] == prefix+'verify':
            if schedDB.find_one({"userID": message.author.id, "action": "verifyCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            for i in range(0, len(message.author.roles)):
                if message.author.roles[i].id == serverDB.find_one({"serverID": message.guild.id})["verificationRole"]:
                    await message.delete()
                    return
            await message.author.add_roles(message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["verificationRole"]), reason='USER VERIFICATION')
            await message.delete()
            await message.author.send(f'You have now been verified in {message.guild.name} Enjoy the server!')
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"verifyCD"})

        #uverify command tree
        elif content[0] == prefix+'uverify':
            if message.author.guild_permissions.administrator:
                if len(content) == 1:
                    await message.delete()
                elif len(message.mentions) <= 0:
                    await message.delete()
                else:
                    for i in range(0, len(message.author.roles)):
                        if message.mentions[0].roles[i].id == serverDB.find_one({"serverID": message.guild.id})["verificationRole"]:
                            await message.delete()
                            return
                    await message.mentions[0].add_roles(message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["verificationRole"]), reason='USER VERIFICATION')
                    await message.delete()

        #setchannel command tree
        elif content[0] == prefix+'setchannel':
            if message.author.guild_permissions.administrator:
                def helpText():
                    embed = discord.Embed(title="__**Set Channel Help**__", description="**Admin only.** Do `"+prefix+"setchannel {channel (welcome, for example)}` to set that channel!", colour=0x32CD32)
                    embed.add_field(name="Botspam", value=f"Sets the bot-spam channel. Find out more with `{prefix}help botspam`")
                    embed.add_field(name="Welcome", value=f"Sets the welcome channel. Find out more with `{prefix}help welcome`")
                    embed.set_footer(text=f"Do `{prefix}help` to find out about what commands there are")
                    return embed
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if len(content) <= 1:
                    await message.channel.send(embed=helpText())
                elif content[1] == 'help':
                    await message.channel.send(embed=helpText())
                else:
                    if content[1] == 'botspam':
                        if message.content[len(prefix)+19:] == '':
                            await message.channel.send('Please mention a channel to set as the bot spam')
                        elif not any(chr.isdigit() for chr in content[2]):
                            await message.channel.send("Please mention a channel to set as the bot spam")
                        elif message.guild.get_channel(int(''.join(filter(str.isdigit, content[2])))) == None:
                            await message.channel.send("Please mention a channel to set as the bot spam")
                        else:
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"botSpamChannel": int(''.join(filter(str.isdigit, content[2])))}})
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"botspamEnabled": True}})
                            await message.channel.send('My bot spam channel for this server has been updated to: <#'+str(serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"])+'>')
                    elif content[1] == 'welcome':
                        if message.content[len(prefix)+19:] == '':
                            await message.channel.send('Please mention a channel to set as the welcome channel')
                        elif not any(chr.isdigit() for chr in content[2]):
                            await message.channel.send("Please mention a channel to set as the welcome channel")
                        elif message.guild.get_channel(int(''.join(filter(str.isdigit, content[2])))) == None:
                            await message.channel.send("Please mention a channel to set as the welcome channel")
                        else:
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"welcomeChannel": int(''.join(filter(str.isdigit, content[2])))}})
                            await message.channel.send('My welcome channel for this server has been updated to: <#'+str(serverDB.find_one({"serverID": message.guild.id})["welcomeChannel"])+'>')
                    else:
                        await message.channel.send(embed=helpText())

        #member setup command tree
        elif content[0] == prefix+'setup':
            if schedDB.find_one({"userID": message.author.id, "action": "setupCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None or invDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
                await message.channel.send('You have been added to our database. Use the `bank` command to check your, well, bank')
            else:
                await message.channel.send("We already have records of your existance. We don't need anymore")
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"setupCD"})

        #daily command tree
        elif content[0] == prefix+'daily':
            if schedDB.find_one({"userID": message.author.id, "action": "dailyCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if schedDB.find_one({"userID": message.author.id, "action": "daily"}) != None:
                timeLeft = schedDB.find_one({"userID": message.author.id, "action": "daily"})["timeLeft"]
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
                schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "daily",
                                   "timeLeft": 86400,
                                   "bot": client.user.id})
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"dailyCD"})
                
        #bank command tree
        elif content[0] == prefix+'bank':
            if schedDB.find_one({"userID": message.author.id, "action": "bankCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            def helpText():
                embed = discord.Embed(title="__**Bank Help**__", description="Do `"+prefix+"bank {action (balance, for example)}` to do that actiion!", colour=0x32CD32)
                embed.add_field(name="Balance (bal)", value=f"Check how much {currency} you (or someone else) have! Can also be done using `{prefix}bal`")
                embed.add_field(name="Transfer", value=f"Give some cash money moolah to a friend(or not) of yours! Just ping the person after the command")
                embed.set_footer(text=f"Do `{prefix}help currency` to find out more about the currency system")
                return embed
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if len(content) <= 1:
                await message.channel.send(embed=helpText())
            elif content[1] == 'help':
                await message.channel.send(embed=helpText())
            elif 'balance' == content[1] or 'bal' == content[1]:
                if message.content[len(prefix)+4:] == '': 
                    await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency)
                else:
                    if len(message.mentions) == 0:
                        await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency)
                        return
                    ping = message.mentions[0]
                    if ping.id == message.author.id:
                        await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency+'\nYou dont need to ping yourself to find out your balance btw')
                    elif currencyDB.find_one({"userID": ping.id}) == None:
                        await message.channel.send('I cannot find that person in my database')
                    else:
                        await message.channel.send('They have '+str(currencyDB.find_one({"userID": ping.id})["birbSeed"])+' '+currency)
            elif 'transfer' == content[1]:
                if len(content) <= 2:
                    await message.channel.send("Who do you want to transfer to? \nIf you ping nobody, I should just take the money for myself")
                    return
                elif len(message.mentions) == 0:
                    await message.channel.send("Who do you want to transfer to? \nIf you ping nobody, I should just take the money for myself")
                    return
                ping = message.mentions[0]
                if ping.id == message.author.id:
                    await message.channel.send("You can't transfer money to yourself. \nI thought that would be kinda obvious")
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
                    if len(content) <= 3:
                        await message.channel.send("Nothing isn't a form of currency I'm programmed to support")
                    elif content[3].isdigit():
                        ammount = content[3]
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
                                if int(ammount) == 1:
                                    sendMessage = f"You just gave {ammount} {currency} to <@{pingID}>! It's a nice gesture, but why bother when it's only 1?"
                                if int(ammount) < 100:
                                    await message.channel.send(f"You just gave {ammount} {currency} to <@{pingID}>! How *generous*")
                                else:
                                    await message.channel.send(f"You just gave {ammount} {currency} to <@{pingID}>! How generous!")
                    else:
                        await message.channel.send("Either something went wrong, or you're trying to transfer somebody a word. \nThat's what DM's are for")
            else:
                await message.channel.send(embed=helpText())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"bankCD"})

        #work command tree
        elif content[0] == prefix+'work':
            if schedDB.find_one({"userID": message.author.id, "action": "workCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if schedDB.find_one({"userID": message.author.id, "action": "work"}) != None:
                await message.channel.send("You already have a work request set up. Pick a number between 1 and 5.")
            elif schedDB.find_one({"userID": message.author.id, "action": "workTimer"}) != None :
                timeLeft = schedDB.find_one({"userID": message.author.id, "action": "workTimer"})["timeLeft"]
                seconds = timeLeft % (24 * 3600)
                hour = seconds // 3600
                seconds = seconds % 3600
                minutes = seconds // 60
                seconds = seconds % 60
                await message.channel.send("Too soon! You cannot work again for another "+str(hour)+':'+str(minutes)+':'+str(seconds))
            else:
                schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "work",
                                   "timeLeft": 10,
                                   "bot": client.user.id})
                await message.channel.send("Pick a number between 1 and 5")
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"workCD"})
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "work"}) != None:
            if content[0] in ['1', '2', '3', '4', '5']:
                num = random.randint(0,5)
                if content[0] == '1':
                    if num == 1:
                        num2 = random.randint(100,1000)
                        ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                        updatedAmmount = ammount+num2
                        currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                        sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky!"
                        await message.channel.send(sendMessage)
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 in [27340, 39666]:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+75000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 75k has been added to your bank"
                            await message.channel.send(sendMessage)
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 in [34474, 20714, 12502]:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+50000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 50k has been added to your bank"
                            await message.channel.send(sendMessage)
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                        elif num2 in [11294, 5112, 20033, 38827, 21014]:
                            ammount = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            updatedAmmount = ammount+num2+25000
                            currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": updatedAmmount}})
                            sendMessage = "You did some work and earned yourself "+str(num2)+" "+currency+". \nCoveniently, all of it went directly into your bank, as there are no taxes in this digital world. Lucky! \nBut that's not all! on your way home, you got a scratch card and won! An aditional 25k has been added to your bank"
                            await message.channel.send(sendMessage)
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                            schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                            schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
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
                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                        schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "workTimer",
                                   "timeLeft": 10800,
                                   "bot": client.user.id})
                else:
                    await message.channel.send("Something went wrong. I don't know what. Chances are, the dev doesn't either")
                    schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
            else:
                await message.channel.send("You haven't entered a number matching the criteria")
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "work"})
                return
        
        #easier bank balance command
        elif message.content.startswith(prefix+'bal'):
            if schedDB.find_one({"userID": message.author.id, "action": "balCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if message.content[len(prefix)+4:] == '' or len(message.mentions) == 0: 
                if currencyDB.find_one({"userID": message.author.id}) == None:
                    userSetup(message.author.id)
                await message.channel.send('You have '+str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])+' '+currency)
            else:
                ping = message.mentions[0]
                if ping.id == message.author.id:
                    if currencyDB.find_one({"userID": message.author.id}) == None:
                        userSetup(message.author.id)
                    await message.channel.send(f'You have {str(currencyDB.find_one({"userID": message.author.id})["birbSeed"])} {currency}\n(You dont need to ping yourself to find out your balance)')
                else:
                    if currencyDB.find_one({"userID": ping.id}) == None:
                        userSetup(ping.id)
                    await message.channel.send('They have '+str(currencyDB.find_one({"userID": ping.id})["birbSeed"])+' '+currency)
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"balCD"})

        #shop command tree
        elif content[0] == prefix+'shop':
            if schedDB.find_one({"userID": message.author.id, "action": "shopCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            def helpText():
                    embed = discord.Embed(title="__**Shop Help**__", description="Do `"+prefix+"shop {action (inv, for example)}` to do that action!", colour=0x32CD32)
                    embed.add_field(name="Inventory (inv)", value=f"Do this one to find out what the shop is selling")
                    embed.add_field(name="Item", value=f"Do `"+prefix+"shop item {number}` (number found in shop inv) to find out more about a specific item")
                    embed.add_field(name="Buy", value=f"Buy an item by doing `"+prefix+"shop buy {number} {optional ammount}`")
                    embed.add_field(name="Sell", value=f"Sell an item by doing `"+prefix+"shop sell {number} {optional ammount}`")
                    embed.add_field(name="Transfer", value=f"Transfer an item to a friend by doing `"+prefix+"shop transfer {ping your mate} {number} {optional ammount}`")
                    embed.add_field(name="Throw (bin, trash)", value=f"Throw away an item(s) by doing `"+prefix+"shop throw {number} {optional ammount}`")
                    embed.set_footer(text=f"Do `{prefix}help` to find out about what commands there are")
                    return embed
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if len(content) <= 1:
                await message.channel.send(embed=helpText())
            elif content[1] == 'help':
                await message.channel.send(embed=helpText())
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
                if len(content) <= 2:
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
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send('Please enter a valid item number')
            elif 'buy' == content[1]:
                if len(content) <= 2:
                    await message.channel.send("Please provide a valid item number to buy")
                    return
                num = 0
                for a in range(1,12):
                    if str(a) == content[2]:
                        if len(content) <= 3:
                            num = 1
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
                if len(content) <= 2:
                    await message.channel.send("Please provide an item number to sell")
                else:
                    for i in range(1,24):
                        if content[2] == str(i):
                            if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                await message.channel.send("You don't own any of this item. In which case, you cannot sell it")
                            else:
                                #await message.channel.send(message.content[(len(prefix)+len(str(content[2]))+10):])
                                if len(content) <= 3:
                                    num = 1
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
            elif 'transfer' == content[1]:
                if len(content) <= 3:
                    await message.channel.send("Please provide an item number to transfer")
                elif len(message.mentions) < 1:
                    await message.channel.send("Please mention somebody to transfer the item too")
                else:
                    if currencyDB.find_one({"userID": message.mentions[0].id}) == None or invDB.find_one({"userID": message.mentions[0].id}) == None:
                        userSetup(message.mentions[0].id)
                    for i in range(1,24):
                        if content[3] == str(i):
                            if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                await message.channel.send("You don't own any of this item. In which case, you cannot transfer it")
                            else:
                                if len(content) <= 4:
                                    num = 1
                                elif content[4].isdecimal() == True:
                                    num = int(content[4])
                                else: num = 1
                                amount = invDB.find_one({"userID": message.author.id})[str(content[3])]
                                amount2 = invDB.find_one({"userID": message.mentions[0].id})[str(content[3])]
                                if amount < num:
                                    await message.channel.send("You don't have the required amount of items. And you cannot transfer air")
                                else:
                                    invDB.find_one_and_update({"userID": message.author.id},{"$set":{str(content[3]):(amount-num)}})
                                    invDB.find_one_and_update({"userID": message.mentions[0].id},{"$set":{str(content[3]):(amount+num)}})
                                    name = invDB.find_one({"list": "name"})[str(content[3])]
                                await message.channel.send(f"You have successfully transfered {num} {name} to <@{message.mentions[0].id}>!")
            elif content[1] in ("trash", "bin","throw"):
                if len(content) <= 2:
                    await message.channel.send("Please provide an item number to throw away")
                else:
                    for i in range(1,24):
                        if content[2] == str(i):
                            if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                await message.channel.send("You don't own any of this item. In which case, you cannot throw it away")
                            else:
                                if len(content) <= 3:
                                    num = 1
                                elif content[3].isdecimal() == True:
                                    num = int(content[3])
                                else: num = 1
                                amount = invDB.find_one({"userID": message.author.id})[str(content[2])]
                                if amount < num:
                                    await message.channel.send("You don't have the required amount of items. And you cannot throw away air")
                                else:
                                    invDB.find_one_and_update({"userID": message.author.id},{"$set":{str(content[2]):(amount-num)}})
                                    price = invDB.find_one({"list": "price"})[str(content[2])]
                                    name = invDB.find_one({"list": "name"})[str(content[2])]
                                    await message.channel.send(f"You have successfully thrown away {num} {name}\n(*You could've earned {int(price)*int(num)} if you sold them. Why not do that next time?*)")
            else:
                await message.channel.send(embed=helpText())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"shopCD"})

        #help command tree
        elif content[0] in [prefix+'help', '$help']:
            if schedDB.find_one({"userID": message.author.id, "action": "helpCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            def baseHelp():
                embed = discord.Embed(title = "__**Welcome to RoBirb!**__", description = f"What do I do? Well, what do I not do? | My prefix in this server is {prefix}", colour=0x32CD32)
                embed.add_field(name='__Moderation Features__', value=prefix+'help moderation', inline=True)
                embed.add_field(name='__Currency Features__', value=prefix+'help currency', inline=True)
                embed.add_field(name='__Gambling Features__', value=prefix+"help gambling", inline=True)
                embed.add_field(name='__Fun Features__', value=prefix+"help fun", inline=True)
                embed.add_field(name='__Random Features__', value=prefix+"help random", inline=True)
                embed.add_field(name='__Future Features__', value=prefix+"help future", inline=True)
                embed.add_field(name='__Festive Features__', value=prefix+"help christmas", inline=True)
                embed.set_footer(text='A website is currently being worked on for this. It will have an interactive help system ')
                return embed
            if len(content) == 1:
                await message.channel.send(embed=baseHelp())
            elif content[1] == 'moderation':
                embed=discord.Embed(title = "__**Moderation Commands**__", description=f"This is a list of all the moderation commands to help you fend off the bad", colour=0x32CD32)
                def baseMod():
                    embed.add_field(name="__Page 1__", value=f"Do `{prefix}help moderation 2` for page 2")
                    embed.add_field(name=f"{prefix}kick", value=f"Kicks a pinged user", inline= False)
                    embed.add_field(name=f"{prefix}ban", value="Bans a pinged user", inline= False)
                    embed.add_field(name=f"{prefix}setrole", value=f"Sets recorded roles for this server. Do `{prefix}setrole help` for more", inline= False)
                    embed.add_field(name=f"{prefix}setchannel", value=f"Sets recorded channels for this server. Do `{prefix}setchannel help` for more", inline= False)
                    embed.add_field(name=f"__Sub-Systems__", value="Complicated moderation things", inline= False)
                    embed.add_field(name=f"Verificaton", value=f"{prefix}help verification", inline= False)
                    embed.add_field(name=f"Bot Spam", value=f"{prefix}help botspam", inline= False)
                    embed.add_field(name=f"Welcome", value=f"{prefix}help welcome", inline= False)
                    embed.add_field(name=f"Muting", value=f"{prefix}help mute", inline= False)
                if len(content) <= 2:
                    baseMod()
                elif content[2] == "1":
                    baseMod()
                elif content[2] == "2":
                    embed.add_field(name="__Page 2__", value=f"Do `{prefix}help moderation 1` for page 1")
                    embed.add_field(name=f"{prefix}setmessage", value=f"Sets recorded messages for this server. Do `{prefix}setmessage help` for more", inline= False)
                    embed.add_field(name=f"{prefix}warn", value=f"Warns a user. Including a reason is optional, but recommended", inline = False)
                    embed.add_field(name=f"{prefix}warnings (warns)", value=f"Lists all warnings recorded in this server. Do `{prefix}warnings help` for more search options", inline = False)
                    embed.add_field(name=f"{prefix}removewarn (deletewarn)", value=f"Removes either a specified warning, or all warrnings for a pinged user", inline = False)
                    embed.add_field(name=f"{prefix}lockdown", value=f"Prevents @everyone (or the verification role, if set) from sending messages in the channel the message was sent in", inline = False)
                    embed.add_field(name=f"{prefix}unlockdown", value=f"Allows @everyone (or the verification role, if set) to send messages in the channel the message was sent in", inline = False)
                else: baseMod()
                embed.set_footer(text="Think we should add more? DM the bot (we probably wont check) or use the $botsuggest command. Most of these commands have respective \"help\" subcommands")
                await message.channel.send(embed=embed)
            elif content[1] == 'currency':
                embed=discord.Embed(title = "__**Currency Commands**__", description=f"This is a list of all the currency commands that give and take away your {currency}", colour=0x32CD32)
                embed.add_field(name=f"{prefix}bank", value=f"It's just a bank. You can check yours (or someone elses) {currency} balance and transfer somebody an amount of {currency}. `{prefix}bank help`", inline= False)
                embed.add_field(name=f"{prefix}bal", value=f"Easier bank balance command. Can find out how much {currency} you (or someone else) has", inline= False)
                embed.add_field(name=f"{prefix}shop", value=f"A shop. You can spend {currency} to obtain something, or sell something to obtain {currency}. `{prefix}shop help`", inline= False)
                embed.add_field(name=f"{prefix}daily", value=f"Gives you free {currency}. Can only be used once a day, obviously", inline= False)
                embed.add_field(name=f"{prefix}work", value=f"Work to earn {currency}. Can be done once every 3 hours. (Might be improved in the future, unsure)", inline= False)
                embed.add_field(name=f"{prefix}merchant (m)", value=f"Some old guy, who we don't know, wanders through here every now and then. He buys and sells things for some good, and sometimes bad, amounts of{currency}", inline= False)
                embed.add_field(name=f"{prefix}rob (bankrob)", value=f"Can rob your ~~fri~~enemys. But be careful, there are repercussions if you get caught", inline= False)
                embed.add_field(name=f"{prefix}inventory (inv)", value=f"See your inventory, and what items you've bought with your {currency}", inline= False)
                embed.set_footer(text="Think we should add more? DM the bot (we probably wont check) or use the $botsuggest command. Most of these commands have respective \"help\" subcommands")
                await message.channel.send(embed=embed)
            elif content[1] == 'gambling':
                embed=discord.Embed(title = "__**Gambling Commands**__", description=f"This is a list of all the gambling commands that make you loose all your easy earned {currency}", colour=0x32CD32)
                embed.add_field(name=f"{prefix}rps (rockpaperscissors)", value="Simple ol' rock paper scissors. "+prefix+"rps {'r', 'p' or 's'} {bet ammount}`", inline= False)
                embed.add_field(name=f"{prefix}hilo (hl, highlow)", value="You'll be given a number, and need to guess if the second hidden number is higher or lower than it. `"+prefix+"hilo {bet ammount}", inline= False)
                embed.add_field(name=f"{prefix}roulette", value=f"This was a pain. It is just \"basic\" roulette. Do `{prefix}roulette help` to find out more. *There is a lot. Be warned.*", inline= False)
                embed.add_field(name=f"{prefix}blackjack", value="This is disfunctional right now. I'll probably get around to it later", inline= False)
                embed.add_field(name=f"{prefix}slotmachine (sm)", value="This is disfunctional right now. I'll probably get around to it later", inline= False)
                embed.set_footer(text="Think we should add more? DM the bot (we probably wont check) or use the $botsuggest command. All of these commands have respective \"help\" subcommands")
                await message.channel.send(embed=embed)
            elif content[1] == 'fun':
                embed=discord.Embed(title = "__**Fun Commands**__", description="This is a list of all the fun commands, that don't really serve much purpose", colour=0x32CD32)
                embed.add_field(name=f"{prefix}kill", value="Ping the person you want to kill after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}slaughter", value="Ping the person you want to slaughter after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}hug", value="Ping the person you want to hug after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}punch", value="Ping the person you want to punch after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}kiss", value="Ping the person you want to kiss after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}slap", value="Ping the person you want to slap after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}bslap", value="Ping the person you want to birch slap *~~family friendly~~* after the command. Or not, up to you", inline= False)
                embed.add_field(name=f"{prefix}cuddle", value="Ping the person you want to cuddle after the command. Or not, up to you", inline= False)
                embed.set_footer(text="Think we should add more? DM the bot (we probably wont check) or use the $botsuggest command")
                await message.channel.send(embed=embed)
            elif content[1] == 'random':
                embed=discord.Embed(title = "__**Random Commands**__", description=f"This is a list of all the random commands that serves many, or no, purpose", colour=0x32CD32)
                embed.add_field(name=f"{prefix}setup", value=f"Sets up a profile for you in our database. Only needs to be done once. *Your data is mine*", inline= False)
                embed.add_field(name=f"{prefix}serversetup", value="**Admin only.** Sets up a profile for this server in our database. Only needs to be done once. *Your data is more mine*", inline= False)
                embed.add_field(name=f"{prefix}setcurrency", value="**Admin only.** Sets the currency name for this server. Default is birbseed.", inline= False)
                embed.add_field(name=f"{prefix}invite", value=f"Sends the bots invite link", inline= False)
                embed.add_field(name=f"{prefix}ping", value="Sends the bots ping", inline= False)
                embed.add_field(name=f"{prefix}hello", value=f"Hello!", inline= False)
                embed.add_field(name=f"{prefix}help", value=f"You need to read this?", inline= False)
                embed.add_field(name=f"{prefix}dmme", value=f"Hello! *But this time it's personal*", inline= False)
                embed.set_footer(text="Think we should add more? DM the bot (we probably wont check) or use the $botsuggest command. Some of these commands have respective \"help\" subcommands")
                await message.channel.send(embed=embed)
            elif content[1] == 'future':
                embed=discord.Embed(title = "__**Future Commands**__", description=f"This is a list of all the Future commands which are currently being worked on", colour=0x32CD32)
                embed.add_field(name=f"Pet system", value=f"The current pet system, but more beefy. Aka, a battle system, strengh, health, and other cool things", inline= False)
                embed.add_field(name=f"A website", value=f"I know it isn't a command, but it's still cool", inline= False)
                embed.add_field(name=f"More gambling commands", value="Gimme your {currency}", inline= False)
                embed.add_field(name=f"More moderation commands", value=f"Fend off the bad, but better!", inline= False)
                embed.add_field(name=f"Gathering and crafting system", value=f"The big kahoona. The big mamba jamba. Why the hell did I decide to take on such a large project. More details will be released at a later date", inline= False)
                embed.add_field(name=f"XP and level system", value=f"You know it from every other bot out there. The only difference being that I don't know how to impliment it and, I'm assuming, they do", inline= False)
                embed.set_footer(text="Think we should add more? (please don't) DM the bot (we probably wont check) or use the $botsuggest command. Some of these commands have respective \"help\" subcommands")
            elif content[1] == 'help':
                await message.channel.send("`* Clever. Verrrryyy clever.` \n`* You think you're really smart, don't you?` \n`* You did a command which you thought wouldn't get a response. Which you thought I hadn't have thought about` \n`* But no. I've thought of it. I've thought of everything. There is nothing you can do which won't muster a response from me`")
            elif content[1] == 'me':
                await message.channel.send("I can do many things, but this is not one of them")
            elif content[1] == 'verification':
                embed=discord.Embed(title = "__**Verification System**__", description="What the verification system is, and how to set it up", colour=0x32CD32)
                embed.add_field(name=f"__General Premice:__", value="The verification system is designed to stop bot accounts from being able to send messages and raid. Requires a role that stops @everyone from sending messages in any/all channels. You must do that, I cannot", inline= False)
                embed.add_field(name=f"* {prefix}setrole verification", value="Sets the role the following commands give", inline= False)
                embed.add_field(name=f"{prefix}verify", value="Gives the user the verification role. Command message deletes itself after sent", inline= False)
                embed.add_field(name=f"*{prefix}uverify", value="Ping a user after this command to verify them. Command message deletes itself after sent", inline= False)
                embed.set_footer(text="* = Admin Only")
                await message.channel.send(embed=embed)
            elif content[1] == 'botspam':
                embed=discord.Embed(title = "__**Bot-Spam System**__", description="What the bot-spam system is, and how to set it up", colour=0x32CD32)
                embed.add_field(name=f"__General Premice:__", value="The bot-spam system is capable of recording edited and deleted messages, and sends an embed within the \"bot-spam channel\" whenever a message is edited or deleted. Muting the channel is greatly recommended", inline= False)
                embed.add_field(name=f"{prefix}setchannel botspam", value="Sets the channel the records get sent in *(botspam gets set to enabled when this channel is set)*", inline= False)
                embed.add_field(name=f"{prefix}botspam enable/disable", value="Enables or disables the botspam system", inline= False)
                embed.set_footer(text="All commands are admin only")
                await message.channel.send(embed=embed)
            elif content[1] == 'welcome':
                embed=discord.Embed(title = "__**Welcome System**__", description="What the welcome system is, and how to set it up", colour=0x32CD32)
                embed.add_field(name=f"__General Premice:__", value="The welcome system is a system which is capable of sending a message when someone joins this server, or when someone leaves", inline= False)
                embed.add_field(name=f"{prefix}setchannel welcome", value="Sets the channel where the welcome and leave messages are sent", inline= False)
                embed.add_field(name=f"{prefix}setmessage welcome/leave", value="Sets the welcome or leave messages", inline= False)
                embed.add_field(name=f"{prefix}welcometest", value="Sends the welcome message in the channel the message is sent", inline= False)
                embed.add_field(name=f"{prefix}leavetest", value="Sends the leave message in the channel the message is sent", inline= False)
                embed.add_field(name=f"{prefix}welcome enable/disable", value="Enables or disables the welcome system", inline= False)
                embed.set_footer(text="All commands are admin only")
                await message.channel.send(embed=embed)
            elif content[1] == 'mute':
                embed=discord.Embed(title="__**Mute System**__", description="Can mute and unmute users", colour=0X32CD32)
                embed.add_field(name=f"{prefix}setrole mute", value=f"Sets the mute role. It does not have to be set; it is made automatically when the {prefix}mute command is first used (if unset)", inline = False)
                embed.add_field(name=f"{prefix}mute", value=f"Ping the person you want to mute after this. If it doesn't work, make sure the bots role is above the mute role in the role hierarchy", inline = False)
                embed.add_field(name=f"{prefix}unmute", value=f"Ping the person you want to unmute after this. Can't unmute people who were muted by different bots", inline = False)
                embed.set_footer(text="All commands are admin only")
                await message.channel.send(embed=embed)
            elif content[1] == 'christmas':
                embed = discord.Embed(title="__Christmas Help__", description="Help for all the Christmassy commands!", colour=0x32CD32)
                embed.add_field(name=f"The Leaderboard", value=f"Every year, a new leaderboard will be made for this. Whoever has the highest score (times you've hit people minus times you've been hit) in the world by the end of December wins a prize!", inline = False)
                embed.add_field(name=f"{prefix}christmasify", value=f"Makes you more christmassy! (Gives you an entry on the leaderboard so you can actually participate. Can only be used once)", inline = False)
                embed.add_field(name=f"{prefix}collect", value=f"Collects snowballs that you can throw at others! Can only be done once every 5 minuets, and you can get between 5 and 50", inline = False)
                embed.add_field(name=f"{prefix}throw", value=f"Yeet a snowball into your friends face! Ping them after the command to do so", inline = False)
                embed.add_field(name=f"{prefix}stats", value=f"Shows what your snowy stats are!", inline = False)
                embed.add_field(name=f"{prefix}leaderboard", value=f"Shows this servers leaderboard (30s cooldown due to server strain)", inline = False)
                embed.add_field(name=f"{prefix}globalleaderboard (gleaderboard)", value=f"Shows the global leaderboard (3m cooldown due to server strain)", inline = False)
                embed.set_footer(text="These can only be used during the month of December, for obvious reason")
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(embed=baseHelp())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"helpCD"})
                
        #botspam command tree
        elif content[0] in [prefix+'botspam', prefix+'bot-spam']:
            if message.author.guild_permissions.administrator:
                if len(content) == 1:
                    await message.channel.send("Please send a valid subcommand. (`enable`, `disable`)")
                elif content[1] == "enable":
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"botspamEnabled": True}})
                    await message.channel.send("The bot-spam system for this server has been enabled")
                elif content[1] == "disable":
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"botspamEnabled": False}})
                    await message.channel.send("The bot-spam system for this server has been disabled")
                else:
                    await message.channel.send("Please send a valid subcommand. (`enable`, `disable`)")
                    
        #welcomoe command tree
        elif content[0] == prefix+'welcome':
            if message.author.guild_permissions.administrator:
                if len(content) == 1:
                    await message.channel.send("Please send a valid subcommand. (`enable`, `disable`)")
                elif content[1] == "enable":
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"welcomeEnabled": True}})
                    await message.channel.send("The welcome system for this server has been enabled")
                elif content[1] == "disable":
                    serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"welcomeEnabled": False}})
                    await message.channel.send("The welcome system for this server has been disabled")
                else:
                    await message.channel.send("Please send a valid subcommand. (`enable`, `disable`)")
                    
        #botsuggest command tree
        elif content[0] == prefix+'botsuggest':
            if schedDB.find_one({"userID": message.author.id, "action": "botSuggestCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if schedDB.find_one({"userID": message.author.id, "action": "botSuggest"}) != None:
                await message.channel.send("You can only suggest one thing every 3 hours")
            elif len(content) == 1:
                await message.channel.send("You can't suggest nothing. We're already doing that")
            else:
                embed = discord.Embed(tile="__New Suggestion__", description=message.content[len(prefix)+10:], colour=0xFF00FF)
                embed.set_author(name=message.author,  icon_url=message.author.avatar_url)
                embed.set_footer(text="Guild Name: "+message.guild.name)
                guild = client.get_guild(id=birbNestID)
                message2 = await guild.get_channel(botSuggestChannel).send(embed=embed)
                await message.channel.send("Your suggestion has been recorded. Thanks!")
                await message2.add_reaction("👍")
                await message2.add_reaction("👎")
                schedDB.insert_one({"timeLeft": 10800, "action": "botSuggest", "userID": message.author.id})
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"botSuggestCD"})    
            
        #kill command tree
        elif content[0] == prefix+'kill':
            if len(content) == 1:
                await message.channel.send(f'<@{message.author.id}> kills the air!')
            elif len(message.mentions) == 0:
                await message.channel.send(f'<@{message.author.id}> kills the air!')
            else:
                await message.channel.send(f'<@{message.author.id}> kills <@{message.mentions[0].id}>')
                
        #slaughter command tree
        elif content[0] == prefix+'slaughter':
            if len(content) == 1:
                await message.channel.send(f'<@{message.author.id}> brings down an absolute masacare onto the air molecules!')
            elif len(message.mentions) == 0:
                await message.channel.send(f'<@{message.author.id}> brings down an absolute masacare onto the air molecules!')
            elif message.mentions[0].id == ownerID and message.author.id == ownerID:
                await message.channel.send("My owner is trying to slaughter himself? \nGuess I'm going back to updaten't!")
            elif message.mentions[0].id == ownerID and message.author.id != ownerID:
                await message.channel.send(f'<@{message.author.id}> tries to slaughter <@'+str(ownerID)+'> but, with him being my developer, it is in my best interest to keep him alive. \n-slaughters <@{message.author.id}> btw- :)')
            else:
                await message.channel.send(f'<@{message.author.id}> brings down an absolute masacare onto <@{message.mentions[0].id}>')
                
        #hug command tree
        elif content[0] == prefix+'hug':
            if len(content) == 1:
                await message.channel.send(f'-Gives <@{message.author.id}> a big robotic hug-')
            elif len(message.mentions) == 0:
                await message.channel.send(f'-Gives <@{message.author.id}> a big robotic hug-')
            else:
                await message.channel.send(f'<@{message.author.id}> gives <@{message.mentions[0].id}> a big hug!')
                
        #punch command tree
        elif content[0] == prefix+'punch':
            if len(content) == 1:
                await message.channel.send(f'-punches <@{message.author.id}>-')
            elif len(message.mentions) == 0:
                await message.channel.send(f'-punches <@{message.author.id}>-')
            else:
                await message.channel.send(f'<@{message.author.id}> punches <@{message.mentions[0].id}>!')
                
        #kiss command tree
        elif content[0] == prefix+'kiss':
            if len(content) == 1:
                await message.channel.send('I\'ll take a pass on this one')
            elif len(message.mentions) == 0:
                await message.channel.send('I\'ll take a pass on this one')
            else:
                await message.channel.send(f'<@{message.author.id}> gives <@{message.mentions[0].id}> a kiss!')
                
        #slap command tree
        elif content[0] == prefix+'slap':
            if len(content) == 1:
                await message.channel.send(f"-slaps <@{message.author.id}>-")
            elif len(message.mentions) == 0:
                await message.channel.send(f"-slaps <@{message.author.id}>-")
            else:
                await message.channel.send(f"<@{message.author.id}> slaps <@{message.mentions[0].id}>!\nOuch!")
        
        #bitch slap command tree
        elif content[0] in [prefix+'bslap', prefix+'bitchslap', prefix+'birtchslap']:
            if len(content) == 1:
                await message.channel.send(f"-birtch slaps <@{message.author.id}>-\nThat'll leave a mark!")
            elif len(message.mentions) == 0:
                await message.channel.send(f"-slaps <@{message.author.id}>-")
            else:
                await message.channel.send(f"<@{message.author.id}> birtch slaps <@{message.mentions[0].id}>!\nThat must've stung!")
        
        #cuddle command tree
        elif content[0] == prefix+'cuddle':
            if len(content) == 1:
                await message.channel.send('I\'ll take a pass on this one')
            elif len(message.mentions) == 0:
                await message.channel.send('I\'ll take a pass on this one')
            else:
                await message.channel.send('<@'+str(message.author.id)+'> gives <@'+str(message.mentions[0].id)+'> a big hug!')
                
        #rps command tree
        elif content[0] in [prefix+'rps', prefix+'rockpaperscissors']:
            if schedDB.find_one({"userID": message.author.id, "action": "rpsCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if message.content[len(prefix)+3:] == '':
                await message.channel.send("__Rock Paper Scissors__ \nIt's literally just rock paper scissors. Rock beats scissors, paper beats rock and scissors beats paper. \nIf you win the game, you get some amount of currency back \nUsage: `"+prefix+"rps {'r'. 'p' or 's'} {ammount}`")
            elif content[1] == 'help':
                await message.channel.send("__Rock Paper Scissors__ \nIt's literally just rock paper scissors. Rock beats scissors, paper beats rock and scissors beats paper. \nIf you win the game, you get some amount of currency back \nUsage: `"+prefix+"rps {'r'. 'p' or 's'} {ammount}`")
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
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rpsCD"})
        
        #roulette command tree
        elif content[0] == prefix+'roulette' or content[0] == prefix+'r':
            if schedDB.find_one({"userID": message.author.id, "action": "rouletteCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            def helpText():
                    embed = discord.Embed(title="__**Roulette Help**__", description="Do `"+prefix+"roulette (r) {action (add, for example)}` to do that action!", colour=0x32CD32)
                    embed.add_field(name="Start", value=f"Starts a roulette game, as long as there is no game currently going on in this server")
                    embed.add_field(name="Add {ammount} {bet}", value=f"Adds a bet if there is a roulette game currently going on in this server")
                    embed.add_field(name="__Bets__", value=f"Below here are all the possible bet types",inline=False)
                    embed.add_field(name="Row", value=f"0,00   Win ratio is 17 to 1")
                    embed.add_field(name="Split {number1} {number2}", value=f"Any two adjoining numbers vertical or horizontal eg:(1,2  5,8  etc) | 17 to 1 ")
                    embed.add_field(name="Street {first number of street}", value=f"Any three numbers horizontal (1, 2, 3 or 4, 5, 6, etc.)   11 to 1")
                    embed.add_field(name="Corner {number1} {2} {3} {4}", value=f"Any four adjoining numbers in a block (1, 2, 4, 5 or 17, 18, 20, 21, etc.) | 8 to 1")
                    embed.add_field(name="Basket", value=f"0, 00, 1, 2, 3   6 to 1")
                    embed.add_field(name="Double street {first number of first street}", value=f"Any six numbers from two horizontal rows (1, 2, 3, 4, 5, 6 or 28, 29, 30, 31, 32, 33 etc.) | 5 to 1")
                    embed.add_field(name="Column {1,2,3}", value=f"Three vertical columns (1,4,7,10...  2,5,8,11...  3,6,9,12...) | 2 to 1")
                    embed.add_field(name="Dozen {1,2,3}", value=f"The three dozens (1-12, 13-24, 25-36) | 2 to 1")
                    embed.add_field(name="Odd", value=f"Odd numbers | 1 to 1")
                    embed.add_field(name="Even", value=f"Even numbers | 1 to 1")
                    embed.add_field(name="Red", value=f"Red numbers | 1 to 1")
                    embed.add_field(name="Black", value=f"Black numbers | 1 to 1")
                    embed.add_field(name="Half {1,2}", value=f"Two halfs of the board (1-18, 19-36 | 1 to 1")
                    embed.add_field(name="Straight Up", value=prefix+"r add {amount} {number (1,2,3...36)} | 35 to 1")
                    embed.set_image(url='https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg')
                    embed.set_footer(text=f"Do `{prefix}help` to find out about what commands there are")
                    return embed
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if len(content) == 1:
                await message.channel.send(embed=helpText())
            elif content[1] == 'help':
                await message.channel.send(embed=helpText())
            elif message.content[len(prefix)+3:] == '':
                await message.channel.send(embed=helpText())
            else:
                if content[1] == "start":
                    if gambleDB.find_one({"action": "roulette", "guild": message.guild.id}) == None:
                        await message.channel.send(f"A Roulette game has been started. Do `{prefix}r add` to bet some {currency}\nThe wheel will be spun in 5 minuets")
                        ID = random.randint(1000000000000000,9999999999999999)
                        schedDB.insert_one({"timeLeft": 360, "action": "roulette", "id": ID, "guild": message.guild.id})
                        gambleDB.insert_one({"action": "roulette", "id": ID, "guild": message.guild.id, "channel": message.channel.id})
                        await asyncio.sleep(360)
                        num = random.randint(0,38)
                        var1 = True
                        await message.channel.send("The wheel has been spun! \nAll the people who entered have been DM'd how much they won or lost")
                        wins = 0
                        losses = 0
                        while var1:
                            if gambleDB.find_one({"id": ID, "action": "rouletteBet"}) == None:
                                var1 == False
                                gambleDB.find_one_and_delete({"id": ID, "action":"roulette"})
                                await message.channel.send(f"There were {wins} winners and {losses} losers")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
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
                                        await user.send(f"You won the roulette! {winnings} birbseed has been added to your bank. \nYou now have {bal+winnings} birbseed")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                                    else:
                                        losses+=1
                                        await user.send("You did not win the roulette. Better luck next time")
                                        gambleDB.find_one_and_delete({"author":author, "id":ID, "bet": betType})
                    else:
                        timeLeft = schedDB.find_one({"action": "roulette", "guild": message.guild.id})["timeLeft"]
                        await message.channel.send("A Roulette game is already in progress in this server. Do `"+prefix+"add` to bet some "+currency+"\n There is "+str(timeLeft)+" seconds left in this game")
                elif content[1] == "add":
                    if message.content[len(content[0])+len(content[1])+1:] == '':
                        await message.channel.send(embed=helpText())
                    elif message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                        await message.channel.send(embed=helpText())
                    elif content[2] == '' or content[2].isdecimal() == False:
                        await message.channel.send("Please provide an ammount to gamble with")
                    elif int(content[2]) > currencyDB.find_one({"userID": message.author.id})["birbSeed"]:
                        await message.channel.send("You have insufficient funds for the operation")
                    elif int(content[2]) == 0:
                        await message.channel.send("You cant gamble nothing. That also means you'll win nothing")
                    elif gambleDB.find_one({"action": "roulette", "guild": message.guild.id}) == None:
                        await message.channel.send(f"There is no active roulette game for this guild. \nDo `{prefix}r start`")
                    else:
                        if content[3] == "row":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "split":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+1:] == "":
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[5].isdecimal() == False or content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `split {number1} {number2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            if int(content[4]) in [1,4,7,10,13,16,19,22,25,28,31,34]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) - 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                    return
                            elif int(content[4]) in [2,5,8,11,14,17,20,23,26,29,32,35]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) - 1 != int(content[4]) and int(content[5]) + 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                    return
                            elif int(content[4]) in [3,6,9,12,15,18,21,24,27,30,33,36]:
                                if int(content[5]) - 3 != int(content[4]) and int(content[5]) + 1 != int(content[4]) and int(content[5]) + 3 != int(content[4]):
                                    await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                    schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                    return
                            else:
                                await message.channel.send("With splits, the two numbers need to be next to each other (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg)")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return                                
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = int(content[2])
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id,"number1": int(content[4]), "number2": int(content[5])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "street":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+1:] == "":
                                await message.channel.send("Command usage = `street {first number of street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `street {first number of street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `street {first number of street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
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
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "corner":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+4:] == "":
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+len(content[5])+5:] == "":
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+len(content[5])+len(content[6])+6:] == "":
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            elif content[4].isdecimal() == False:
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                await message.channel.send("Command usage = `corner {value 1} {2} {3} {4}`")
                                return
                            arr = [int(content[4]), int(content[5]), int(content[6]), int(content[7])]
                            if arr not in [[1,2,4,5],[2,3,5,6],[4,5,7,8],[5,6,8,9],[7,8,10,11],[8,9,11,12],[10,11,13,14],[11,12,14,15],[16,17,19,20],[17,18,20,21],[19,20,22,23],[20,21,23,24],[22,23,25,26],[23,24,26,27],[25,26,28,29],[26,27,29,30],[28,29,31,32],[29,30,32,33],[31,32,34,35],[32,33,35,36]]:
                                await message.channel.send("A corner needs to be four numbers in a square, (https://cdn.w600.comps.canstockphoto.com/american-style-roulette-wheel-and-table-drawing_csp87098496.jpg) \nI.e. 1 2 4 5 or 22 23 25 26 \n*if all 4 numbers are in a square, make sure theyre in ascending order (lo-hi)*")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "numbers": arr})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "basket":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "double":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+1:] == "":
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+len(content[4])+1:] == "":
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[5].isdecimal() == False:
                                await message.channel.send("Command usage = `double street {first number of first street}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
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
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[5])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "column":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2 and int(content[4]) != 3:
                                await message.channel.send("Command usage = `column {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "dozen":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2 and int(content[4]) != 3:
                                await message.channel.send("Command usage = `dozen {1,2 or 3}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "odd":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "even":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "red":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "black":
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        elif content[3] == "half":
                            if message.content[len(content[0])+len(content[1])+len(content[2])+len(content[3])+3:] == "":
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[4].isdecimal() == False:
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            if int(content[4]) != 1 and int(content[4]) != 2:
                                await message.channel.send("Command usage = `half {1 or 2}`")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            ID = gambleDB.find_one({"action": "roulette", "guild": message.guild.id})["id"]
                            bet = content[2]
                            oldBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                            newBal = oldBal-int(bet)
                            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
                            timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                            gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id, "number": int(content[4])})
                            await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                        else:
                            if message.content[len(content[0])+len(content[1])+1:] == "":
                                await message.channel.send("Please input a valid bet name")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[2].isdecimal() == False:
                                await message.channel.send("Please input a valid bet name")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif message.content[len(content[0])+len(content[1])+len(content[2])+1:] == "":
                                await message.channel.send("Please input a valid amount")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                                return
                            elif content[3].isdecimal() == False:
                                await message.channel.send("Please input a valid amount")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
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
                                    timeLeft = schedDB.find_one({"id": ID})["timeLeft"]
                                    gambleDB.insert_one({"action": "rouletteBet", "id": ID,"bet": content[3], "amount": int(bet), "author": message.author.id})
                                    await message.channel.send("Your bet has been placed. Good luck \nThe wheel will be spun in "+str(timeLeft)+" seconds")
                else: await message.channel.send(embed=helpText())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"rouletteCD"})
                
        #blackjack command tree
        elif content[0] == prefix+'blackjack':
            return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if message.content[len(prefix)+3:] == '':
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
        elif content[0] == prefix+'slotmachine' or content[0] == prefix+'smachine' or content[0] == prefix+'sm':
            return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if message.content[len(prefix)+3:] == '':
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
        elif content[0] == prefix+'highlow' or content[0] == prefix+'hl' or content[0] == prefix+'hilo':
            if schedDB.find_one({"userID": message.author.id, "action": "hiloCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if message.content[len(content[0]):] == '' or content[1].isdecimal() == False:
                await message.channel.send("Please provide an ammount to gamble with \n`"+prefix+"hilo {ammount}`")
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
                schedDB.insert_one({"userID": message.author.id,
                                   "channel": message.channel.id,
                                   "guild": message.guild.id,
                                   "action": "hilo",
                                   "timeLeft": 10,
                                   "bot": client.user.id,
                                   "result": num3,
                                   "number": num2,
                                   "bet": content[1]})
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"hiloCD"})
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "hilo"}) != None:
            guess1 = content[0].lower()
            result = schedDB.find_one({"userID": message.author.id, "action": "hilo"})["result"]
            number = schedDB.find_one({"userID": message.author.id, "action": "hilo"})["number"]
            bet = schedDB.find_one({"userID": message.author.id, "action": "hilo"})["bet"]
            if guess1 == 'hi' or guess1 == 'high' or guess1 == 'h' or guess1 == 'higher':
                guess = 1
            elif guess1 == 'lo' or guess1 == 'low' or guess1 == 'l' or guess1 == 'lower':
                guess = 2
            else:
                await message.channel.send("Incorrect command usage")
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
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
                    await message.channel.send(f"You win. The number was higher. \n{win} {currency} has been added to your bank \nThe number was {number}")
                    schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 2:
                    await message.channel.send(f"You lose. The number was higher. \n{bet} {currency} has been withdrawn from your bank \nThe number was {number}")
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    newBal = prevBal-int(bet)
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 3:
                    return
            elif result == 2:
                if guess == 1:
                    await message.channel.send(f"You lose. The number was higher. \n{bet} {currency} has been withdrawn from your bank \nThe number was {number}")
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    newBal = prevBal-int(bet)
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 2:
                    prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    if prevBal >= 10000000:
                        win = int(int(bet)/(prevBal/10000000))
                    else:
                        win = int(bet)
                    newBal = prevBal+win
                    currencyDB.find_one_and_update({"userID": message.author.id}, {"$set":{"birbSeed": newBal}})
                    await message.channel.send(f"You win. The number was higher. \n{win} {currency} has been added to your bank \nThe number was {number}")
                    schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                elif guess == 3:
                    return
            elif result == 3:
                await message.channel.send("The numbers were the same. Your bank ballance will also stay the same")
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "hilo"})
                
        #coinflip command tree
        elif content[0] in [prefix+"coinflip", prefix+"cf", prefix+"fiftyfifty", prefix+"50/50", prefix+"5050"]:
            return
            
        #invite command tree
        elif content[0] == prefix+'invite':
            await message.channel.send("Invite link for me: \nhttps://discord.com/api/oauth2/authorize?client_id=730483800626167818&permissions=8&scope=bot")
            
        #rob command tree
        elif content[0] == prefix+'rob' or content[0] == prefix+'bankrob':
            if schedDB.find_one({"userID": message.author.id, "action": "robCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            if (message.content[len(content[0]):] == '') or (message.mentions == 0 or None):
                await message.channel.send("Incorrect command usage\n`"+prefix+"rob {person}`")
            elif len(message.mentions) <= 0:
                await message.channel.send("You cannot rob an object")
            elif currencyDB.find_one({"userID": message.mentions[0].id}) == None:
                await message.channel.send("Your ~~fri~~enemy has no bank that you can steal out of. I ain't letting you steal their possesions \nTough luck")
            elif currencyDB.find_one({"userID": message.mentions[0].id})["birbSeed"] == 0:
                await message.channel.send("Your ~~fri~~enemy has no money for you to steel. I ain't letting you steal their possesions \nTough luck")
            elif message.mentions[0].id == message.author.id:
                await message.channel.send("You cannot rob yourself.")
            #elif schedDB.find_one({"userID": message.mentions[0].id, "action": "robCool"}) != None:
            #    timeLeft = schedDB.find_one({"userID": message.mentions[0].id, "action": "robCool"})["timeLeft"]
            #    seconds = timeLeft % (24 * 3600)
            #    hour = seconds // 3600
            #    seconds = seconds % 3600
            #    minutes = seconds // 60
            #    seconds = seconds % 60
            #    await message.channel.send(f"This person hasn't long been robbed! At least wait another {minutes} minutes and {seconds} seconds!")
            else:
                maximum = 0
                caught = False
                pingID = message.mentions[0].id
                num = random.randint(1,10)
                if num == 1 or num == 2 or num == 3 or num == 10:
                    maximum = (currencyDB.find_one({"userID": pingID})["birbSeed"])/15
                    caught = False
                elif num in [4,5,6,7,8] and currencyDB.find_one({"userID": message.author.id})["birbSeed"] == 0:
                    maximum = 2500
                    caught = True
                elif num == 4 or num == 5 or num == 6 or num == 7 or num == 8:
                    maximum = (currencyDB.find_one({"userID": message.author.id})["birbSeed"])/12
                    caught = True
                elif num == 9:
                    maximum = (currencyDB.find_one({"userID": pingID})["birbSeed"])/8
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
                schedDB.insert_one({"userID": message.mentions[0].id, "timeLeft": 300, "action": "robCool"})
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"robCD"})

        #ping command tree
        elif content[0] == prefix+'ping':
            await message.channel.send("pong")
            latency = client.latency    
            await message.channel.send("Latency: "+str(latency)[2:5]+"ms")

        #setmessage command tree
        elif content[0] == prefix+'setmessage':
            if message.author.guild_permissions.administrator:
                def helpText():
                    embed = discord.Embed(title="__**Set Message Help**__", description="**Admin only.** Do `"+prefix+"setmessage {action (join, for example)}`, then send the message afterwards!", colour=0x32CD32)
                    embed.add_field(name="Join", value=f"Sets the welcome message")
                    embed.add_field(name="Leave", value=f"Sets the leave message")
                    embed.set_footer(text=f"Find out more with `{prefix}help welcome`")
                    return embed
                if len(content) == 1:
                    await message.channel.send(embed=helpText())
                elif content[0] == "help":
                    await message.channel.send(embed=helpText())
                elif content[1] in ["join", "welcome"]:
                    await message.channel.send("What would you like to set this servers join message to? (typing {user} pings the user) \nThis has an automatic 1m timeout")
                    schedDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "setMessage",
                                       "timeLeft": 60,
                                       "bot": client.user.id,
                                       "action2": "join"})
                elif content[1] == "leave":
                    await message.channel.send("What would you like to set this servers leave message to? (typing {user} pings the user) \nThis has an automatic 1m timeout")
                    schedDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "setMessage",
                                       "timeLeft": 60,
                                       "bot": client.user.id,
                                       "action2": "leave"})
                else:
                    await message.channel.send(embed=helpText())
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "setMessage"}) != None:
            action = schedDB.find_one({"userID": message.author.id, "action": "setMessage"})["action2"]
            if action == "join":
                serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"joinMessage": message.content}})
                await message.channel.send("The join message has been updated :thumbsup:")
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})
            elif action == "leave":
                serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"leaveMessage": message.content}})
                await message.channel.send("The leave message has been updated :thumbsup:")
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})
            else:
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "setMessage"})

        #welcometest command tree
        elif content[0] == prefix+"welcometest":
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if serverDB.find_one({"serverID": message.guild.id})["joinMessage"] == "":
                    await message.channel.send(f"There is no welcome message for this server.\nDo `{prefix}setmessage join` to set it")
                else:
                    message1 = serverDB.find_one({"serverID": message.guild.id})["joinMessage"]
                    await message.channel.send(message1.replace("{user}", "<@"+str(message.author.id)+">"))

        #leavetest command tree
        elif content[0] == prefix+"leavetest":
            if message.author.guild_permissions.administrator:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if serverDB.find_one({"serverID": message.guild.id})["leaveMessage"] == "":
                    await message.channel.send(f"There is no leave message for this server.\nDo `{prefix}setmessage leave` to set it")
                else:
                    message1 = serverDB.find_one({"serverID": message.guild.id})["leaveMessage"]
                    await message.channel.send(message1.replace("{user}", "<@"+str(message.author.id)+">"))

        #kick command tree
        elif content[0] == prefix+"kick":
            if message.author.guild_permissions.kick_members:
                if message.content[len(prefix)+5:] == '':
                    await message.channel.send("Memebr not found")
                elif len(message.mentions) == 0:
                    await message.channel.send("Member not found")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to kick that user")
                else:
                    await message.guild.kick(message.mentions[0],reason="ROBIRB KICK COMMAND")
                    await message.channel.send("Successfully kicked <@"+str(message.mentions[0].id)+"> :thumbsup:")

        #ban command tree
        elif content[0] == prefix+"ban":
            if message.author.guild_permissions.ban_members:
                if message.content[len(prefix)+4:] == '':
                    await message.channel.send("Memebr not found")
                elif len(message.mentions) == 0:
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

        #unban command tree
        elif content[0] == prefix+"unban":
            if message.author.guild_permissions.ban_members:
                if message.content[len(prefix)+6:] == '':
                    await message.channel.send("Member not found")
                elif len(message.mentions) == 0:
                    await message.channel.send("Member not found")
                else:
                    await message.guild.unban(message.mentions[0],reason="ROBIRB UNBAN COMMAND")

        #mute command tree
        elif content[0] == prefix+"mute":
            if message.author.guild_permissions.mute_members:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if message.content[len(prefix)+5:] == '':
                    await message.channel.send("Member not found")
                elif len(message.mentions) == 0:
                    await message.channel.send("Member not found")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to mute that user")
                else:
                    muteRole = ''
                    if serverDB.find_one({"serverID": message.guild.id})['muteRole'] == '' or message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})['muteRole']) == None:
                        await message.guild.create_role(name="Muted", reason="ROBIRB COMMAND")
                        roles = message.guild.roles
                        serverDB.find_one_and_update({"serverID": message.guild.id},{"$set":{"muteRole": roles[1].id}})
                        channels = message.guild.text_channels
                        for i in range(0,len(channels)):
                            await channels[i].set_permissions(roles[1], send_messages=False)
                        await message.guild.edit_role_positions({roles[1]:((message.guild.get_member(client.user.id)).top_role.position-1)})
                        muteRole = roles[1]
                    else:
                        muteRole = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["muteRole"])
                    await message.mentions[0].add_roles(message.guild.get_role(int(serverDB.find_one({"serverID": message.guild.id})["muteRole"]))  , reason="USER MUTED")
                    await message.channel.send("Successfully muted <@"+str(message.mentions[0].id)+"> :thumbsup:")
                    
        #unmute command tree
        elif content[0] == prefix+'unmute':
            if message.author.guild_permissions.mute_members:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup(message.guild.id)
                if message.content[len(prefix)+5:] == '':
                    await message.channel.send('Member not found')
                elif len(message.mentions) == 0:
                    await message.channel.send('Member not found')
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions to unmute that user")
                else:
                    muteRole = ''
                    if serverDB.find_one({"serverID": message.guild.id})["muteRole"] == '' or message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})['muteRole']) == None:
                        await message.channel.send("I have not muted anybody in this server")
                    else:
                        muteRole = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["muteRole"])
                        for i in message.mentions[0].roles:
                            if i.id == muteRole.id:
                                await message.mentions[0].remove_roles(i, reason="USER UNMUTED")
                                await message.channel.send("Successfully unmuted <@"+str(message.mentions[0].id)+"> :thumbsup:")
                                return
                        await message.channel.send("I could not unmute that person")
                                             
        #inventory command tree
        elif content[0] == prefix+'inventory' or content[0] == prefix+'inv':
            if schedDB.find_one({"userID": message.author.id, "action": "invCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if invDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            count = 0
            for i in range(1,110):
                count += invDB.find_one({"userID": message.author.id})[str(i)]
            invDB.find_one_and_update({"userID": message.author.id}, {"$set":{"items": count}})
            if invDB.find_one({"userID": message.author.id})["items"] == 0:
                await message.channel.send("Your inventory is empty")
            else:
                #num = {}
                embed = discord.Embed(title = "__Your Inventory__", colour = 0xFA00FF)
                for i in range(1,110):
                    if invDB.find_one({"userID": message.author.id})[str(i)] != 0:
                        #num[i] = invDB.find_one({"userID": message.content.id})[i]
                        embed.add_field(name=invDB.find_one({"list": "name"})[str(i)], value = invDB.find_one({"userID": message.author.id})[str(i)])
                await message.channel.send(embed=embed)
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"invCD"})

        #settings command tree
        elif content[0] == prefix+'settings':
            return #Finish later
            #I can't even remember what I wanted a settings command for
        
        #merchant command tree
        elif content[0] == prefix+'merchant' or content[0] == prefix+'m':
            if schedDB.find_one({"userID": message.author.id, "action": "merchantCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            if currencyDB.find_one({"userID": message.author.id}) == None:
                userSetup(message.author.id)
            #if schedDB.find_one({"userID": "rb.Merchant"}) <= None:
            #    timeLeft = schedDB.find_one({"userID": "rb.Merchant"})["timeLeft"]
            #    seconds = timeLeft % (24 * 3600)
            #    hour = seconds // 3600
            #    seconds = seconds % 3600
            #    minutes = seconds // 60
            #    seconds = seconds % 60
            #    await message.channel.send("There is no merchant right now. Try looking again in "+str(hour)+':'+str(minutes)+':'+str(seconds))
            else:
                if True == False:
                    await message.channel.send("This will never be called. I'm being serious. If, by some miricle, you see this message (on Discord, in the code doesnt count), I will give you £20 - Chris\n(Editing the code then doing it through RoBirb2 doesn't count. Needs to be through RoBirb1)") 
                    #I don't have the patience to drop the entire merchant system down by 4 spaces. May as well put an inaccessable easter egg
                else:
                    #THE NUMBER: values 1 through 23 are for buying, numbers 24 through 46 are for selling
                    #Any given number can be from 1 to 8. If the value is 3,4,5 or 6, the item will not show up (buying)
                    #If no items are shown, then pick a random number between 1 and 23 and show the corrisponding item
                    #If the value is 1 or 2, make the item cheaper than the shop (1 cheaper than 2)
                    #if the value is 7 or 8, make the item more expensive than the shop (7 cheaper than 8)
                    #With selling, for each value, pick a random number between (num/10) and 1.  (item selling cost = half the item cost)
                    #If the original number is between 1 and 4, divide the item selling cost by the random number
                    #If the original number is betweem 5 and 8, multiply the item selling cost by the random number
                    #This is going to take fucking forever      Sidenote: it did not, in fact, take fucking forever
                    if len(content) <= 1:
                        await message.channel.send("\"What can I do for ya, kid?\"\n(`"+prefix+"m buy`,`"+prefix+"m sell`)")
                    elif content[1] == 'buy':
                        if len(content) <= 2:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                        elif content[2] == 'inventory' or content[2] == 'inv':
                            num2 = 0
                            embed = discord.Embed(title = "__Merchants Shop__", description="Do `"+prefix+"shop item {number}` to find out about the item", colour = 0x8F00FF)
                            for i in range(1,12):
                                num = currencyDB.find_one({"userID": "merchant.buy"})[str(i)]
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
                                num = currencyDB.find_one({"userID":"merchant.buy"})[str(num3)]
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
                            if len(content) <= 3:
                                await message.channel.send("\"I ain't selling air, kid!\"\n(Please provide a valid item number)")
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"merchantCD"})
                                return
                            for a in range(1,12):
                                num = currencyDB.find_one({"userID":"merchant.buy"})[str(a)]
                                if str(a) == content[3]:
                                    if num == 3 or num == 4 or num == 5 or num == 6:
                                        await message.channel.send("\"I ain't selling that, kid!\"")
                                        continue
                                    if len(content) <= 4:
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
                                        await message.channel.send("\"You haven't got enough dough!\"")
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
                                        await message.channel.send(f"\"Pleasure doin' buisiness with you, kid!\"\n(You just bought {c} {name.lower()}! You now have {newBal} {currency})")
                        else:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                    elif content[1] == 'sell':
                        if len(content) <= 2:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                        elif content[2] == 'inventory' or content[2] == 'inv':
                            embed = discord.Embed(title = "__Merchants Request List__", description="Basically, this is what he wants to buy, and how much he'll pay per item", colour = 0x39FF14)
                            for i in range(1,12):
                                num = currencyDB.find_one({"userID": "merchant.buy"})[str(i)]
                                num2 = currencyDB.find_one({"userID": "merchant.sell"})[str(i)]
                                price = (int(invDB.find_one({"list":"price"})[str(i)])/2)
                                if num <= 4:
                                    price = price/num2
                                else: price = price*num2
                                embed.add_field(name=str(i)+': '+invDB.find_one({"list":"name"})[str(i)], value=str(int(price)))
                            embed.set_footer(text="Page 1")
                            await message.channel.send(embed=embed)
                        elif content[2] == 'item':
                            if len(content) <= 3:
                                await message.channel.send("\"I ain't buying air, kid!\"\n(Please provide a valid item number)")
                            else:
                                for i in range(1,24):
                                    if content[3] == str(i):
                                        if invDB.find_one({"userID": message.author.id})[str(i)] == 0:
                                            await message.channel.send("\"You don't have any of that, kid!\"")
                                        else:
                                            #await message.channel.send(message.content[(len(prefix)+len(str(content[2]))+10):])
                                            if len(content) <= 4:
                                                num = 1
                                            elif content[4].isdecimal() == True:
                                                num = int(content[4])
                                            else: num = 1
                                            amount = invDB.find_one({"userID": message.author.id})[str(content[3])]
                                            if amount < num:
                                                await message.channel.send("\"You don't have enough of 'em, kid!\"")
                                            else:
                                                num2 = currencyDB.find_one({"userID":"merchant.buy"})[str(i)]
                                                num3 = currencyDB.find_one({"userID": "merchant.sell"})[str(i)]
                                                price = (int(invDB.find_one({"list": "price"})[str(content[3])])/2)
                                                if num2 <= 4:
                                                    price = int(price/num3)
                                                else: price = int(price*num3)
                                                price = price*num
                                                invDB.find_one_and_update({"userID": message.author.id},{"$set":{str(content[3]):(amount-num)}})
                                                prevBal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                                                currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": (prevBal+price)}})
                                                name = invDB.find_one({"list": "name"})[str(content[3])]
                                                await message.channel.send(f"\"Pleasure doin' buisiness with you, kid!\"\n(You just sold {num} {name}! You have earned {price} {currency})")
                        else:
                            await message.channel.send("\"What'll it be?\"\n(inventory, item)")
                    elif content[1] == 'talk':
                        await message.channel.send("\"Well, it seems we have an easter egg hunter on our hands!\"\n\"You're lucky I'm in a good mood.\"\n\"There isn't really a whole lot to say about myself. I don't know how I got here, or where I go when I leave. I just... appear here every once in a while, just waiting for someone like you.\"\n\"It's a strange feeling, phasing in and out of existance. Sometimes I wish I didn't need to return. But, alas, I have not a single bit of choice.\"\n\"But hey, it's not all bad. Pays good! Heheheh\"")
                    else:
                        await message.channel.send("\"What can I do for ya, kid?\"\n(`"+prefix+"m buy`,`"+prefix+"m sell`)")
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"merchantCD"})
            
        #lockdown command tree
        elif content[0] == prefix+'lockdown':
            if message.author.guild_permissions.mute_members:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup()
                if serverDB.find_one({"serverID": message.guild.id})["verificationRole"] == "":
                    role = message.guild.roles[0]
                else: role = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["verificationRole"])
                await message.channel.set_permissions(role, send_messages=False)
                await message.channel.send("This channel has now been locked down. :no_entry_sign:")
                
        #unlockdown command tree
        elif content[0] == prefix+'unlockdown':
            if message.author.guild_permissions.mute_members:
                if serverDB.find_one({"serverID": message.guild.id}) == None:
                    serverSetup()
                if serverDB.find_one({"serverID": message.guild.id})["verificationRole"] == "":
                    role = message.guild.roles[0]
                else: role = message.guild.get_role(serverDB.find_one({"serverID": message.guild.id})["verificationRole"])
                await message.channel.set_permissions(role, send_messages=True)
                await message.channel.send("This channel has now been un-locked down. :white_check_mark:")
                
        #warn command tree
        elif content[0] == prefix+'warn':
            if message.author.guild_permissions.mute_members:
                if len(content) <= 1:
                    await message.channel.send("Usage: `"+prefix+"warn {user} {reason}`\n*Reason is optional, but recommended*")
                elif len(message.mentions) == 0:
                    await message.channel.send("Usage: `"+prefix+"warn {user} {reason}`\n*Reason is optional, but recommended*")
                else:
                    if len(content) <= 2:
                        reason = "None"
                    else: 
                        reason = ""
                        for i in content[2:]:
                            reason+=(i+" ")
                    var = True
                    while var:
                        warnID = random.randint(1111111111111111,9999999999999999)
                        if warnDB.find_one({"warnID": warnID}) == None:
                            var = False
                    warnDB.insert_one({"warnedID": message.mentions[0].id, "authorID": message.author.id, "serverID": message.guild.id, "reason": reason, "time": datetime.datetime.now(), "serverName": message.guild.name, "warnID":warnID})
                    embed = discord.Embed(title="__Warning Successful__", description=f"Successfully warned <@{message.mentions[0].id}>", colour=0xFF0000)
                    embed.add_field(name="__Reason Given__", value=reason, inline=False)
                    embed.set_footer(text=f"By <@{message.author.id}> in {message.guild.name} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    await message.channel.send(embed=embed)
                    
        #warns command tree
        elif content[0] == prefix+'warns' or content[0] == prefix+'warnings':
            if message.author.guild_permissions.mute_members:
                isTime = False
                num = 0
                pageNo = 1
                embed = discord.Embed(title="__Server Warnings__", description=f"Do `{prefix}warnings help` for more search options", colour=0x00D5FF)
                if len(content) <= 1:
                    listVar = {"serverID": message.guild.id}
                elif content[1] == "help":
                    await message.channel.send("Usage: `"+prefix+"warnings [page number and / or search options]`\nSearch options: (for all warnings in this server, put nothing after the command)\n\"by {ping a user}\" = shows all warnings in this server which were made by the pinged user\n\"to {ping a user}\" = shows all warnings in this server which are aimed towards the pinged user\n\"on {date (i.e.2022-07-09)}\" = shows all warnings in this server which were done during the specified day")
                    return
                elif content[1].isdecimal:
                    pageNo = int(content[1])
                if "by" in content:
                    if len(message.mentions) == 0:
                        await message.channel.send(f"No user was pinged\n`{prefix}warnings help`")
                        return
                    else: listVar = {"serverID": message.guild.id, "authorID": message.mentions[0].id}
                elif "to" in content:
                    if len(message.mentions) == 0:
                        await message.channel.send(f"No user was pinged\n`{prefix}warnings help`")
                        return
                    else: listVar = {"serverID": message.guild.id, "warnedID": message.mentions[0].id}
                elif "on" in content:
                    if len(content) <= 2:
                        await message.channel.send(f"No time was specified\n`{prefix}warnings help`")
                        return
                    elif not content[2][0:4].isdecimal() or not content[2][5:7].isdecimal() or not content[2][8:10].isdecimal():
                        await message.channel.send(f"An invalid time was specified\n`{prefix}warnings help`")
                        return
                    else:
                        isTime = True
                        for i in warnDB.find({"serverID": message.guild.id}):
                            if i["time"].year == int(content[2][0:4]) and i["time"].month == int(content[2][5:7]) and i["time"].day == int(content[2][8:10]):
                                embed.add_field(name=f"{num+1}: Warning ID: {i['warnID']} at {i['time'].strftime('%Y-%m-%d %H:%M:%S')}", value=f"<@{i['warnedID']}> by <@{i['authorID']}> | Reason given: {i['reason']}", inline=False)
                                num += 1
                        if num == 0:
                            embed.add_field(name="None", value="None were found")
                    listVar = {"serverID": message.guild.id, "time": content[2]}
                else: listVar = {"serverID": message.guild.id}
                if not isTime:
                    if warnDB.find_one(listVar) == None:
                        embed.add_field(name="None", value="None were found")
                    for i in warnDB.find(listVar):
                        
                        if num >= 10:
                            continue
                        else:
                            embed.add_field(name=f"{num+1}: Warning ID: {i['warnID']} at {i['time'].strftime('%Y-%m-%d %H:%M:%S')}", value=f"<@{i['warnedID']}> by <@{i['authorID']}> | Reason given: {i['reason']}", inline=False)
                        num += 1
                embed.set_footer(text=f"Page {pageNo} of warnings (\"{prefix}warns {pageNo+1}\" for pg{pageNo+1}) in: \"{message.guild.name}\"")
                await message.channel.send(embed=embed)
                
        #removewarn command tree
        elif content[0] == prefix+'removewarn' or content[0] == prefix+'deletewarn':
            if message.author.guild_permissions.mute_members:
                if len(content) <= 1:
                    await message.channel.send("Usage: `"+prefix+"removewarn id {valid warn ID}` (deletes a specific warning) *warnID's found in `"+prefix+"warnings`*\nOR `"+prefix+"removewarn user {ping the user}` (deletes all warnings associated with the pinged user)\n*Fun fact, 'deletewarn' can be used in place of 'removewarn'*")
                elif content[1] == "id":
                    if len(content) <= 2:
                        await message.channel.send("Usage: `"+prefix+"removewarn id {valid warn ID}`\n*Warn ID's can be found by doing `"+prefix+"warnings`*")
                    elif content[2].isdecimal() == False:
                        await message.channel.send("Usage: `"+prefix+"removewarn id {valid warn ID}`\n*Warn ID's can be found by doing `"+prefix+"warnings`*")
                    elif warnDB.find_one({"warnID": int(content[2]), "serverID": message.guild.id}) == None:
                        await message.channel.send("Invalid ID\nUsage: `"+prefix+"removewarn id {valid warn ID}`\n*Warn ID's can be found by doing `"+prefix+"warnings`*")
                    else:
                        warnDB.find_one_and_delete({"warnID": int(content[2])})
                        await message.channel.send("That warning has been removed")
                elif content[1] == "user":
                    if len(message.mentions) == 0:
                        await message.channel.send("Usage: `"+prefix+"removewarn user {ping the user}`")
                    elif warnDB.find_one({"warnedID": message.mentions[0].id, "serverID": message.guild.id}) == None:
                        await message.channel.send("No warnings found in this server for the specified user")
                    else:
                        for i in warnDB.find({"warnedID": message.mentions[0].id, "serverID": message.guild.id}):
                            warnDB.find_one_and_delete({"warnID": i["warnID"]})
                        await message.channel.send("All warnings associated with that user (in this server) have been removed")
                else:
                    await message.channel.send("Usage: `"+prefix+"removewarn id {valid warn ID}` (deletes a specific warning) *warnID's found in `"+prefix+"warnings`*\nOR `"+prefix+"removewarn user {ping the user}` (deletes all warnings associated with the pinged user)\n*Fun fact, 'deletewarn' can be used in place of 'removewarn'*")
            
        #voicemute command tree
        elif content[0] in [prefix+"vmute", prefix+"voicemute"]:
            if message.author.guild_permissions.mute_members:
                if len(message.mentions) == 0:
                    await message.channel.send("No user was specified\n`"+prefix+"vmute {ping the required user}`")
                elif message.mentions[0].VoiceState(mute) == True:
                    await message.channel.send("That user is already voice muted")
                else:
                    await message.mentions[0].edit(mute=True)
                    await message.channel.send("Successfully voice muted that user :thumbsup:")
                    
        #voiceunmute command tree
        elif content[0] in [prefix+"vunmute", prefix+"voiceunmute"]:
            if message.author.guild_permissions.mute_members:
                if len(message.mentions) == 0:
                    await message.channel.send("No user was specified\n`"+prefix+"vunmute {ping the required user}`")
                elif message.mentions[0].VoiceState(mute) == False:
                    await message.channel.send("That user is not voice muted")
                else:
                    await message.mentions[0].edit(mute=False)
                    await message.channel.send("Successfully voice unmuted that user :thumbsup:")
                    
        #voicedeafen command tree
        elif content[0] in [prefix+"vdeafen", prefix+"voicedeafen"]:
            if message.author.guild_permissions.mute_members:
                if len(message.mentions) == 0:
                    await message.channel.send("No user was specified\n`"+prefix+"vdeafen {ping the required user}`")
                elif message.mentions[0].VoiceState(deaf) == True:
                    await message.channel.send("That user is already voice deafened")
                else:
                    await message.mentions[0].edit(deaf=True)
                    await message.channel.send("Successfully voice deafened that user :thumbsup:")
                    
        #voiceundeafen command tree 
        elif content[0] in [prefix+"vundeafen", prefix+"voiceundeafen"]:
            if message.author.guild_permissions.mute_members:
                if len(message.mentions) == 0:
                    await message.channel.send("No user was specified\n`"+prefix+"vundeafen {ping the required user}`") 
                elif message.mentions[0].VoiceState(deaf) == False:
                    await message.channel.send("That user is not voice deafened")
                else:
                    await message.mentions[0].edit(deaf=False)
                    await message.channel.send("Successfully voice undeafened that user :thumbsup:")
                    
        #slowmode command tree
        elif content[0] == prefix+'slowmode':
            if message.author.guild_permissions.manage_channels:
                if len(content) <= 1:
                    await message.channel.send("Slowmode usage: `"+prefix+"slowmode {time (seconds) / off / disable / none} {(optional) channel}`")
                elif content[1] == "help":
                    await message.channel.send("Slowmode usage: `"+prefix+"slowmode {time (seconds) / off / disable / none} {(optional) channel}`")
                #elif content[1] in ("5s","10s","15s","30s","1m","2m","5m","10m","15m","30m","1h","2h","6h"):
                elif content[1].isdigit() or content[1] in ("off","disable","0","none"):
                    if len(content) <= 2:
                        channel = message.channel.id
                    elif not any(chr.isdigit() for chr in content[2]):
                        channel = message.channel.id
                    elif message.guild.get_channel(int(''.join(filter(str.isdigit, content[2])))) == None:
                            channel = message.channel.id
                    else: channel = int(''.join(filter(str.isdigit, content[2])))
                    channel = message.guild.get_channel(channel)
                    seconds = int(content[1])
                    if content[1] in ("off","disable","0","none"):
                        if channel.slowmode_delay == 0:
                            await message.channel.send(f"Slowmode is already disabled in <#{channel.id}>")
                        await channel.edit(slowmode_delay=0)
                        await message.channel.send(f"Slowmode has been disabled in <#{channel.id}>")
                    elif seconds > 21600:
                        await channel.edit(slowmode_delay=21600)
                        await message.channel.send(f"Slowmode has been enabled for its maximum value (6h) in <#{channel.id}>")
                    else:
                        await channel.edit(slowmode_delay=seconds)
                        await message.channel.send(f"Slowmode has been enabled for {seconds} seconds in <#{channel.id}>")
                else: await message.channel.send("Slowmode usage: `"+prefix+"slowmode {time (seconds) / off / disable / none} {(optional) channel}`")
                
        #nick command tree
        elif content[0] in (prefix+"nick", prefix+"nickname", prefix+"name"):
            if len(content) <= 1:
                await message.channel.send("Nickname usage: `"+prefix+"nick {(optional, mod only) pinged user} {name (32 characters)}`")
            elif content[1] == "help":
                await message.channel.send("Nickname usage: `"+prefix+"nick {(optional, mod only) pinged user} {name (32 characters)}`")
            elif len(message.mentions) == 0:
                if content[1] in ("reset","clear"):
                    if message.author.guild_permissions.change_nickname:
                        if message.author.guild_permissions.administrator:
                            await message.channel.send("I don't have the required permissions (or my role isn't elevated enough) for this operation")
                        else: 
                            await message.author.edit(nick="")
                            await message.channel.send("Your nickname has been reset :thumbsup:")
                    else: await message.channel.send("You don't have the required permissions for this operation")
                elif len(message.content[len(prefix)+len(content[0]):]) > 32:
                    await message.channel.send("Maximum characters allowed for a nickname is 32")
                elif message.author.guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions (or my role isn't elevated enough) for this operation")
                elif message.author.guild_permissions.change_nickname:
                    await message.author.edit(nick=message.content[len(prefix)+len(content[0]):])
                    await message.channel.send("Your nickname has been updated :thumbsup:")
                else: await message.channel.send("You don't have the required permissions for this operation")
            elif len(message.mentions) >= 1:
                if content[2] in ("reset","clear"):
                    if message.author.guild_permissions.manage_nicknames:
                        if message.mentions[0].guild_permissions.administrator:
                            await message.channel.send("I don't have the required permissions (or my role isn't elevated enough) for this operation")
                        else: 
                            await message.mentions[0].edit(nick="")
                            await message.channel.send("Their nickname has been reset :thumbsup:")
                elif len(message.content[len(prefix)+len(content[0])+len(content[1])+1:]) > 32:
                    await message.channel.send("Maximum characters allowed for a nickname is 32")
                elif message.mentions[0].guild_permissions.administrator:
                    await message.channel.send("I don't have the required permissions (or my role isn't elevated enough) for this operation")
                elif message.author.guild_permissions.manage_nicknames:
                    await message.mentions[0].edit(nick=message.content[len(prefix)+len(content[0])+len(content[1])+1:])
                    await message.channel.send("Updated their username :thumbsup:")
                else: await message.channel.send("You don't have the required permissions for this operation")
                                    
        #botinfo command tree
        elif content[0] == prefix+"botinfo":
            totalServers = 0
            totalUsers = 0
            totalPets = 0
            totalColours = 0
            totalWarnings = 0
            for i in serverDB.find():
                totalServers += 1
            for i in currencyDB.find():
                if i["userID"] in ("merchant.sell", "merchant.buy"):
                    continue
                else: totalUsers += 1
            for i in petDB.find():
                if i["userID"] == "pet.list":
                    continue
                else: totalPets += 1
            for i in colourDB.find():
                totalColours += 1
            for i in warnDB.find():
                totalWarnings += 1
            embed = discord.Embed(title="__RoBirb Bot Information__", description="Some random statistics about the bot",colour=0x30D5C8)
            embed.add_field(name="__No. servers with the bot__", value=f"Currently infesting {len(client.guilds)} servers")
            embed.add_field(name="__Total servers to ever add the bot__", value=f"Managed to infest {totalServers} servers in total")
            embed.add_field(name="__Total no. users to ever register with the bot__", value=f"{totalUsers} users have registered")
            embed.add_field(name="__No. pets owned through the bot__", value=f"{totalPets} pets owned through the bot")
            embed.add_field(name="__No. colours registered through the bot__", value=f"{totalColours} colours registered through the bot (all servers)")
            embed.add_field(name="__No. warnings delt through the bot__", value=f"{totalWarnings} warnings delt through the bot (all servers)")
            await message.channel.send(embed=embed)
            
        #pet command tree
        elif content[0] == prefix+'pet':
#            if schedDB.find_one({"userID": message.author.id, "action": "petCD"}) != None:
#                await message.channel.send(f"Please wait before using this command again")
#                return
            def helpText():
                    embed = discord.Embed(title="__**Pet Help**__", description=" Do `"+prefix+"pet {subcommand (list, for example)}` to do that thing!", colour=0x32CD32)
                    embed.add_field(name="List", value=f"Lists all the pets available to purchace")
                    embed.add_field(name="Info", value=f"Shows info on an individual animal")
                    embed.add_field(name="Buy", value=f"Buy a pet")
                    embed.add_field(name="Inventory (inv)", value=f"See all pets you own")
                    #embed.add_field(name="Abandon", value=f"Abandon your pet :(")
                    #embed.add_field(name="Sell", value=f"Sell your pet :(")
                    embed.add_field(name="Train", value=f"Train your pet. Make 'em stronk")
                    embed.add_field(name="Stats", value=f"See the statistics of a pet you own")
                    embed.add_field(name="Feed", value=f"Feed a pet you own")
                    embed.add_field(name="Water", value=f"Water a pet you own")
                    embed.add_field(name="Play", value=f"Play with your pet. Make 'em happy")
                    #embed.add_field(name="Battle", value=f"Battle two pets!")
                    embed.set_footer(text=f"Do `{prefix}help` to find out about different commands")
                    return embed
            if message.content[len(content[0]):] == '':
                await message.channel.send(embed=helpText())
            elif content[1] == "help":
                await message.channel.send(embed=helpText())
            elif content[1] == "list":
                embed = discord.Embed(title="**__Available Pets__**",description="Pets available to purchace. Find out more with `"+prefix+"pet info {pet type}`", colour = 0xF000FF)
                for i in range(1,25):
                    embed.add_field(name=petDB.find_one({"type":"name"})[str(i)],value=petDB.find_one({"type":"price"})[str(i)])
                await message.channel.send(embed=embed)
            elif content[1] == "info":
                await message.channel.send("This is a work in progress")
                return #Info of the animals 
            elif content[1] == "buy":
                if message.content[len(content[0])+len(content[1])+1:] == '':
                    await message.channel.send("Command usage: `"+prefix+"pet buy {type (dog, cat, etc)}`")
                    return
                elif currencyDB.find_one({"userID": message.author.id}) == None:
                    userSetup(message.author.id)
                num = 0
                for i in range(1,25):
                    if content[2] == petDB.find_one({"type":"name"})[str(i)]:
                        num = 1
                        typeNum = i
                if num == 1:
                    bal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
                    price = petDB.find_one({"type": "price"})[str(typeNum)]
                    if bal < price:
                        await message.channel.send("You cannot afford them")
                    schedDB.insert_one({"userID": message.author.id,
                                       "channel": message.channel.id,
                                       "guild": message.guild.id,
                                       "action": "petBuy",
                                       "timeLeft": 21,
                                       "bot": client.user.id,
                                       "type": str(content[2]),
                                       "price": price})
                    await message.channel.send("What would you like your pet to be called?\n(Max of 50 characters)")
                    await asyncio.sleep (20)
                    if schedDB.find_one({"userID": message.author.id, "action": "petBuy"}) == None:
                        return                        
                    await message.channel.send("The request timed out")
                else: await message.channel.send("Command usage: `"+prefix+"pet buy {type (dog, cat, etc)}`")
            elif content[1] == "inventory" or content[1] == "inv":
                if petDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("You don't own any pets")
                else:
                    embed = discord.Embed(title="__**Your Pets**__", description="This is a list of all the pets you own!", colour = 0x00BFFF)
                    for i in petDB.find({"userID": message.author.id}):
                      embed.add_field(name=f'__{i["dispName"]}__', value=f'{i["gender"]} {i["type"]}', inline=False)
                    await message.channel.send(embed=embed)
            elif content[1] == "abandon":
                return #Maybe have this cost something? Make it have some sort of deterent
            elif content[1] == "sell":
                return #Maybe insted of abandoning them. Actually, I don't know which is worse
            elif content[1] == "train":
                if petDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("You don't own any pets")
                elif len(content) <= 2:
                    await message.channel.send("You didn't add a pet name")
                elif petDB.find_one({"userID": message.author.id, "name": str(content[2:][0])}) == None:
                    await message.channel.send("You don't own a pet called that. Can't train air")
                else:
                    pet = petDB.find_one({"userID": message.author.id, "name": str(content[2:][0])})
                    pronoun1 = "him" if pet["gender"] == "male" else "her"
                    if True == False: return
                    #if pet["hunger"] <= 0.0005:
                    #    await message.channel.send(f"Your pet is too hungry to do this, feed {pronoun1}!")
                    #elif pet["thirst"] <= 0.0007:
                    #    await message.channel.send(f"Your pet is too thirsty to do this, water {pronoun1}!")
                    #elif pet["tiredness"] >= 0.9934:
                    #    await message.channel.send(f"Your pet is too tired to do this, let {pronoun1} rest for a while!")
                    else:
                        embed = discord.Embed(title="__Pet Training__", description=f'You are currently training {pet["dispName"]}', colour = 0x00BFFF)
                        embed.add_field(name="__What would you like to do?__", value=":muscle: Train strength\n:shield: Train defence")
                        message1 = await message.channel.send(embed=embed)
                        await message1.add_reaction("💪")
                        await message1.add_reaction("🛡️")
                        schedDB.insert_one({"userID": message.author.id,"timeLeft": 11, "action":"reactionAdd", "action2":"petTrain1", "emoji": ""})
                        timer = 0
                        trainType = 0
                        trainWord = ""
                        while timer <= 10:
                            trainEmoji = schedDB.find_one({"userID": message.author.id, "action":"reactionAdd", "action2":"petTrain1"})["emoji"]
                            if trainEmoji == "💪":
                                trainType = 1
                                trainWord = "Strength"
                                timer += 100
                            elif trainEmoji == "🛡️":
                                trainType = 2
                                trainWord = "Defence"
                                timer += 100
                            await asyncio.sleep(0.1)
                            timer += 0.1
                        await message1.clear_reactions()
                        schedDB.find_one_and_delete({"userID": message.author.id, "action2": "petTrain1"})
                        if trainType == 0:
                            embed.set_field_at(index=0, name="Timed out", value="Timed out")
                            await message1.edit(embed=embed)
                            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"petCD"})
                            return
                        elif trainType == 1:
                            embed.set_field_at(index=0, name="__Strength Training__", value=f'Train {pet["dispName"]}\'s strength!')
                        elif trainType == 2:
                            embed.set_field_at(index=0, name="__Defence Training__", value=f'Train {pet["dispName"]}\'s defence!')
                        embed.add_field(name="__How it works:__", value=f'Every few seconds, a {trainEmoji} reaction will appear on this message. Click it as fast as you can to train your pet! You\'ll have a max of 10 seconds. Don\'t hit any ❌ though, they\'re bad!', inline=False)
                        embed.add_field(name="__Ready?__", value=f'Click the ✅ to begin!. Say stop (end, exit, cancel, etc) to stop.')
                        await message1.edit(embed=embed)
                        await message1.add_reaction("✅")
                        schedDB.insert_one({"userID": message.author.id,"timeLeft": 11, "action":"reactionAdd", "action2":"petTrain2", "emoji": ""})
                        ready = False
                        timer = 0
                        while timer <= 10:
                            emoji = schedDB.find_one({"userID": message.author.id, "action":"reactionAdd", "action2":"petTrain2"})["emoji"]
                            if emoji == "✅":
                                ready = True
                                timer += 100
                            await asyncio.sleep(0.1)
                            timer += 0.1
                        await message1.clear_reactions()
                        schedDB.find_one_and_delete({"userID": message.author.id, "action2": "petTrain2"})
                        if ready == False:
                            embed.remove_field(index=1)
                            embed.remove_field(index=2)
                            embed.set_field_at(index=0, name="Timed out", value="Timed out")
                            await message1.edit(embed=embed)
                            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"petCD"})
                            return
                        elif ready == True:
                            strikesNum = 0
                            strikes = "🟩🟩🟩"
                            checksHit = 0
                            xpEarned = 0
                            embed.remove_field(index=3)
                            embed.remove_field(index=2)
                            embed.remove_field(index=1)
                            embed.set_field_at(index=0, name=f"__{trainWord} Training__", value="Hit the ✅ asap, but don't hit ❌!", inline=False)
                            embed.add_field(name="__Statistics__", value=f"Strikes: {strikes}  |  No. ✅ hit: {checksHit}  |  Total XP earned: {xpEarned}", inline=False)
                            embed.add_field(name="__Get Ready__", value="Sending \"stop\", getting 3 strikes or playing for 10 minuets will exit the game", inline=False)
                            await message1.edit(embed=embed)
                        gameLoop = True
                        gameTimer = 0
                        schedDB.insert_one({"userID": message.author.id, "channel": message.channel.id, "guild": message.guild.id, "bot": client.user.id, "timeLeft": 600, "action": "petTrainGame"})
                        while gameLoop:
                            await message1.clear_reactions()
                            rand = random.randint(1,5)
                            await asyncio.sleep(rand)
                            gameTimer += rand
                            if random.randint(1,20) < 5:
                                await message1.add_reaction("❌")
                                lose = False
                                timer = 0
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 6, "action":"reactionAdd", "action2":"petTrain3", "emoji": ""})
                                while timer <= 3:
                                    emoji = schedDB.find_one({"userID": message.author.id, "action":"reactionAdd", "action2":"petTrain3"})["emoji"]
                                    if emoji == "❌":
                                        lose = True
                                        timer += 100
                                    await asyncio.sleep(0.1)
                                    gameTimer += 0.1
                                    timer += 0.1
                                if schedDB.find_one({"userID": message.author.id, "action2": "petTrain3"}) != None:
                                    schedDB.find_one_and_delete({"userID": message.author.id, "action2": "petTrain3"})
                                if lose == True:
                                    strikesNum += 1
                                    if strikesNum == 1:
                                        strikes = "🟥🟩🟩"
                                    elif strikesNum == 2:
                                        strikes == "🟥🟥🟩"
                                    elif strikesNum == 3:
                                        strikes = "🟥🟥🟥"
                                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "petTrainGame"})
                                    embed.set_field_at(index=1, name="__Statistics__", value=f"Strikes: {strikes}  |  No. ✅ hit: {checksHit}  |  Total XP earned: {xpEarned}", inline=False)
                                    await message1.edit(embed=embed)
                            else:
                                await message1.add_reaction("✅")
                                win = False
                                xpAdd = 0
                                timer = 0
                                schedDB.insert_one({"userID": message.author.id,"timeLeft": 6, "action":"reactionAdd", "action2":"petTrain3", "emoji": ""})
                                while timer <= 5:
                                    emoji = schedDB.find_one({"userID": message.author.id, "action":"reactionAdd", "action2":"petTrain3"})["emoji"]
                                    if emoji == "✅":
                                        win = True
                                        xpAdd = int(500/timer)
                                        xpEarned += xpAdd
                                        checksHit += 1
                                        timer += 100
                                    await asyncio.sleep(0.1)
                                    gameTimer += 0.1
                                    timer += 0.1
                                if schedDB.find_one({"userID": message.author.id, "action2": "petTrain3"}) != None:
                                    schedDB.find_one_and_delete({"userID": message.author.id, "action2": "petTrain3"})
                                if win == True:
                                    embed.set_field_at(index=1, name="__Statistics__", value=f"Strikes: {strikes}  |  No. ✅ hit: {checksHit}  |  Total XP earned: {xpEarned}", inline=False)
                                    await message1.edit(embed=embed)
                                else:
                                    strikesNum += 1
                                    if strikesNum == 1:
                                        strikes = "🟥🟩🟩"
                                    elif strikesNum == 2:
                                        strikes == "🟥🟥🟩"
                                    elif strikesNum == 3:
                                        strikes = "🟥🟥🟥"
                                        schedDB.find_one_and_delete({"userID": message.author.id, "action": "petTrainGame"})
                                    embed.set_field_at(index=1, name="__Statistics__", value=f"Strikes: {strikes}  |  No. ✅ hit: {checksHit}  |  Total XP earned: {xpEarned}", inline=False)
                                    await message1.edit(embed=embed)
                            if schedDB.find_one({"userID": message.author.id, "action": "petTrainGame"}) == None: gameLoop = False
                        await message1.clear_reactions()
                        embed.set_field_at(index=2, name="__Game Over__", value="That was fun. Play again soon!")
                        await message1.edit(embed=embed)
                        if trainWord == "Defence":
                            petDB.find_one_and_update({"petID": pet["petID"]},{"$set":{"defenceXP": xpEarned+pet["defenceXP"]}})
                        else:
                            petDB.find_one_and_update({"petID": pet["petID"]},{"$set":{"strengthXP": xpEarned+pet["strengthXP"]}})
            elif content[1] == "stats":
                if petDB.find_one({"userID": message.author.id}) == None:
                    await message.channel.send("You don't own any pets")
                elif petDB.find_one({"userID": message.author.id, "name": str(content[2:][0])}) == None:
                    await message.channel.send("You don't own a pet called that")
                else:
                    pet = petDB.find_one({"userID": message.author.id, "name": str(content[2:][0])})
                    embed = discord.Embed(title=f"__**{pet['dispName']}**__", description=f"This is the details about your pet!", colour = 0x00BFFF)
                    embed.add_field(name=f"__Name:__ ", value=pet["dispName"])
                    embed.add_field(name=f"__Type:__ ", value=pet["type"])
                    embed.add_field(name=f"__Gender:__ ", value=pet["gender"])
                    embed.add_field(name=f"__Age:__ ", value=pet["age"])
                    embed.add_field(name=f"__Strength:__ ", value=pet["strength"])
                    embed.add_field(name=f"__Defence:__ ", value=pet["defence"])
                    embed.add_field(name=f"__Hunger:__ ", value=pet["hunger"])
                    embed.add_field(name=f"__Thist:__ ", value=pet["thirst"])
                    embed.add_field(name=f"__Level:__ ", value=pet["level"])
                    embed.set_footer(text=f"Some of these values may not currently be used. They will be in a future update!")
                    await message.channel.send(embed=embed)
            elif content[1] == "feed":
                return #Have pet food in the shop. Make the pets requier semi-constant attention. Have the hunger level deplete overtime...somehow
            elif content[1] == "water":
                return #Same as feed, but with water
            elif content[1] == "play":
                return #Play with the pets. Make 'em hapi
            elif content[1] == "battle":
                return #Unsure. Would be interesting, but would also be an absolute pain in the arse
            else:
                await message.channel.send(embed=helpText())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"petCD"})
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "petTrainGame"}) != None:
            if content[0] in ["stop","quit","exit","end","cancel"]:
                schedDB.find_one_and_delete({"userID": message.author.id, "action": "petTrainGame"})
        elif schedDB.find_one({"userID": message.author.id,"channel": message.channel.id, "guild": message.guild.id, "action": "petBuy"}) != None:
            if len(message.content) > 50:
                await message.channel.send("Your pets name cannot be more than 50 characters long")
            var = True
            while var:
                petID = random.randint(1111111111111111,9999999999999999)
                if petDB.find_one({"petID": petID}) == None:
                    var = False
            bal = currencyDB.find_one({"userID": message.author.id})["birbSeed"]
            newBal = bal-schedDB.find_one({"userID": message.author.id, "action": "petBuy"})["price"]
            currencyDB.find_one_and_update({"userID": message.author.id},{"$set":{"birbSeed": int(newBal)}})
            gender = random.randint(1,2)
            if gender == 1:
                gender = "Male"
            else: gender = "Female"
            petDB.insert_one({"userID": message.author.id,
                              "type": schedDB.find_one({"userID": message.author.id, "action": "petBuy"})["type"],
                              "name": str(message.content.lower()),
                              "dispName": str(message.content),
                              "petID": petID,
                              "gender": str(gender),
                              "age": 0,
                              "strength": 0,
                              "strengthXP": 0,
                              "defence": 0,
                              "defenceXP": 0,
                              "hunger": 0,
                              "thirst": 0,
                              "level": 0,
                              "happiness": 0,
                              "tiredness": 0})
            await message.channel.send("You have successfully purchased \""+message.content+"\"!")
            schedDB.find_one_and_delete({"userID": message.author.id,"action": "petBuy"})
            
        #colour command tree
        elif content[0] == prefix+'colour' or content[0] == prefix+'color':
            if schedDB.find_one({"userID": message.author.id, "action": "colourCD"}) != None:
                await message.channel.send(f"Please wait before using this command again")
                return
            def helpText():
                    embed = discord.Embed(title="__**Colour Help**__", description=" Do `"+prefix+"colour {subcommand (list, for example)}` to do that thing! **(Both colour and color work in this command)**", colour=0x32CD32)
                    embed.add_field(name="Setup", value=f"**Admin Only.** `{prefix}colour setup help`")
                    embed.add_field(name="List", value=f"Lists all available colours")
                    embed.add_field(name="Set", value=f"Sets your colour")
                    embed.add_field(name="Remove", value="Removes your colour")
                    embed.set_footer(text=f"Do `{prefix}help` to find out about different commands")
                    return embed
            if message.content[len(content[0]):] == '':
                await message.channel.send(embed=helpText())
            elif content[1] == "help":
                await message.channel.send(embed=helpText())
            elif content[1] == "setup":
                if message.author.guild_permissions.administrator:
                    def helpText2():
                        embed = discord.Embed(title="__**Colour Setup Help**__", description=" Do `"+prefix+"colour {subcommand (list, for example)}` to do that thing! **(Both colour and color work in this command)**", colour=0x32CD32)
                        embed.add_field(name="Add", value=f"Adds a colour. Ping the role to add after the command")
                        embed.add_field(name="Addmany", value=f"Adds many colours. Ping the roles you want to add after the command")
                        embed.add_field(name="Remove", value=f"Removes a colour. Ping the role you want to remove after the command")
                        embed.add_field(name="Removemany", value=f"Removes many colours. Ping the roles you want to remove after the command")
                        embed.add_field(name="Removeall", value="Removes all colours")
                        embed.set_footer(text=f"Do `{prefix}help` to find out about different commands")
                        return embed
                    if message.content[len(content[0])+len(content[1])+1:] == '':
                        await message.channel.send(embed=helpText2())
                    elif content[2] == "add":
                        if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                            await message.channel.send("Please input a role to add to the colours")
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input a role to add to the colours")
                        if colourDB.find_one({"roleID": message.role_mentions[0].id}) != None:
                            await message.channel.send("That role has already been added")
                        else:
                            numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                            colourDB.insert_one({"roleID": message.role_mentions[0].id,
                                                 "hex": str(message.role_mentions[0].colour),
                                                 "name": message.role_mentions[0].name,
                                                 "serverID": message.guild.id,
                                                 "colourNum": numColours+1})
                            numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"numColours": numColours+1}})
                            await message.channel.send("That role has now been added")
                    elif content[2] == "addmany":
                        if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                            await message.channel.send("Please input at least one role to add to the colours")
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input at least one role to add to the colours")
                        else:
                            num = 0
                            num2 = 0
                            numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                            for i in message.role_mentions:
                                if colourDB.find_one({"roleID": i.id}) == None:
                                    colourDB.insert_one({"roleID": i.id,
                                                         "hex": str(i.colour),
                                                         "name": i.name,
                                                         "serverID": message.guild.id,
                                                         "colourNum": numColours+num+1})
                                    num += 1
                                else: num2 += 1
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"numColours": numColours+num}})
                            await message.channel.send(f"{num} roles were added successfully\n{num2} roles could not be added")
                    elif content[2] == "remove":
                        if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                            await message.channel.send("Please input a role to remove from the colours")
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input a role to remove from the colours")
                        elif colourDB.find_one({"roleID": message.role_mentions[0].id}) == None:
                            await message.channel.send("That role is not in the database")
                        else:
                            colourDB.find_one_and_delete({"roleID":message.role_mentions[0].id})
                            numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"numColours": numColours-1}})
                            await message.channel.send("That role has been removed")
                    elif content[2] == "removeall":
                        for i in colourDB.find({"serverID": message.guild.id}):
                            colourDB.find_one_and_delete({"roleID": i["roleID"]})
                        serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"numColours": 0}})
                        await message.channel.send("All colours were removed")
                    elif content[2] == "removemany":
                        if message.content[len(content[0])+len(content[1])+len(content[2])+2:] == '':
                            await message.channel.send("Please input at least one role to remove from the colours")
                        elif len(message.role_mentions) == 0:
                            await message.channel.send("Please input at least one role to remove from the colours")
                        else:
                            num = 0
                            num2 = 0
                            numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                            for i in message.role_mentions:
                                if colourDB.find_one({"roleID": i.id}) != None:
                                    colourDB.find_one_and_delete({"roleID": i.id})
                                    num += 1
                                else: num2 += 1
                            serverDB.find_one_and_update({"serverID": message.guild.id}, {"$set":{"numColours": numColours-num}})
                            await message.channel.send(f"{num} roles were removed successfully\n{num2} roles could not be removed")
                    else: await message.channel.send(embed=helpText2())
            elif message.content[len(content[0]):] == '':
                await message.channel.send(embed=helpText())
            elif colourDB.find_one({"serverID": message.guild.id}) == None:
                await message.channel.send("This guild does not have a setup colour system")
            elif content[1] == "list":
                var = True
                embed = discord.Embed(title = "__Colour List__", description = "The colours available in this server")
                numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                for i in range(0,numColours):
                    embed.add_field(name = str(i+1),value = "<@&"+str(colourDB.find_one({"serverID": message.guild.id, "colourNum": i+1})["roleID"])+">")
                embed.set_footer(text = "Do `"+prefix+"colour set {colour number}` to set your colour!")
                await message.channel.send(embed=embed)
            elif content[1] == "set":
                if len(content) < 2:
                    await message.channel.send("Please input a colour number to get\nDo `"+prefix+"colour list` to see the available colours")
                elif content[2].isdecimal() == False:
                    await message.channel.send("Please input a colour number to get\nDo `"+prefix+"colour list` to see the available colours")
                else:
                    numColours = serverDB.find_one({"serverID": message.guild.id})["numColours"]
                    if int(content[2]) <= 0:
                        await message.channel.send("Please input a colour number to get\nDo `"+prefix+"colour list` to see the available colours")
                    elif int(content[2]) <= numColours:
                        for o in colourDB.find({"serverID": message.guild.id}):
                            for i in message.author.roles:
                                if i.id == o["roleID"]:
                                    await message.author.remove_roles(i, reason="ROBIRB COLOUR COMMAND")
                        await message.author.add_roles(message.guild.get_role(colourDB.find_one({"serverID": message.guild.id, "colourNum": int(content[2])})["roleID"]), reason="ROBIRB COLOUR COMMAND")
                        await message.channel.send("Your colour has now been set to \""+colourDB.find_one({"serverID": message.guild.id, "colourNum": int(content[2])})["name"]+"\"!")
                    else: await message.channel.send("Colour not found")
            elif content[1] == "remove":
                for o in colourDB.find({"serverID": message.guild.id}):
                    for i in message.author.roles:
                        if i.id == o["roleID"]:
                            await message.author.remove_roles(i, reason="ROBIRB COLOUR COMMAND")
                await message.channel.send("Your colour has been removed")
            else: await message.channel.send(embed=helpText())
            schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"colourCD"})
            
            
                            
        #Below here is the crafting and gathering system.
        #Here-on-forth is where I lose my shit
        #---Proceed With Caution---
        
        #Sike. Not happening just yet
                
        elif datetime.datetime.now().month != 11:
            #------------------
            #Christmas Commands
            #------------------
            
            def christmasHelp():
                embed = discord.Embed(title="__Christmas Help__", description="Help for all the Christmassy commands!", colour=0x32CD32)
                embed.add_field(name=f"The Leaderboard", value=f"Every year, a new leaderboard will be made for this. Whoever has the highest score (times you've hit people minus times you've been hit) in the world by the end of December wins a prize!", inline = False)
                embed.add_field(name=f"{prefix}christmasify", value=f"Makes you more christmassy! (Gives you an entry on the leaderboard so you can actually participate. Can only be used once)", inline = False)
                embed.add_field(name=f"{prefix}collect", value=f"Collects snowballs that you can throw at others! Can only be done once every 5 minuets, and you can get between 5 and 50", inline = False)
                embed.add_field(name=f"{prefix}throw", value=f"Yeet a snowball into your friends face! Ping them after the command to do so", inline = False)
                embed.add_field(name=f"{prefix}stats", value=f"Shows what your snowy stats are!", inline = False)
                embed.add_field(name=f"{prefix}leaderboard", value=f"Shows this servers leaderboard (30s cooldown due to server strain)", inline = False)
                embed.add_field(name=f"{prefix}globalleaderboard (gleaderboard)", value=f"Shows the global leaderboard (3m cooldown due to server strain)", inline = False)
                embed.set_footer(text="These can only be used during the month of December, for obvious reason")
                return embed
            
            def christmassy(user):
                    christmasDB.insert_one({"userID": user.id, "userName": user.name, "discriminator": user.discriminator, "snowBalls": 0, "hits": 0, "timesHit": 0, "misses":0})
            
            #christmashelp command tree
            if content[0] in [prefix+"christmashelp", prefix+"chelp", prefix+"cmhelp"]:
                await message.channel.send(embed=christmasHelp())
    
            #christmasify command tree
            elif content[0] == prefix+"christmasify":
                if schedDB.find_one({"userID": message.author.id, "action": "christmasifyCD"}) != None:
                    await message.channel.send(f"Please wait before using this command again")
                    return
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                    #christmasDB.insert_one({"userID": message.author.id, "userName": message.author.name, "discriminator": message.author.discriminator, "snowBalls": 0, "hits": 0, "timesHit": 0, "misses":0})
                    await message.channel.send("You are even more christmassy now!")
                else:
                    await message.channel.send("You're already as christmassy as can be!")
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"christmasifyCD"})
    
            #collect command tree
            elif content[0] == prefix+'collect':
                if schedDB.find_one({"userID": message.author.id, "action": "collectCD"}) != None:
                    await message.channel.send(f"Please wait before using this command again")
                    return
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                if schedDB.find_one({"userID":message.author.id, "action":"ballCollect"}) != None:
                    timeLeft = schedDB.find_one({"userID": message.author.id, "action":"ballCollect"})["timeLeft"]
                    minutes = timeLeft // 60
                    seconds = timeLeft % 60
                    await message.channel.send(f"Your hands are still cold from last time! Come back in {minutes}:{seconds} to get more!")
                else:
                    num = random.randint(5, 50)
                    balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                    balls = balls + num
                    christmasDB.find_one_and_update({"userID":message.author.id}, {"$set":{"snowBalls": balls}})
                    await message.channel.send(f"You have collected {num} snowballs. You now have {balls} snowballs. \nUse `{prefix}throw` to throw a snowball at a \"*friend*\"!")
                    schedDB.insert_one({"userID": message.author.id, "action": "ballCollect", "timeLeft": 300})
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"collectCD"})

            #throw command tree
            elif content[0] == prefix+"throw":
                if schedDB.find_one({"userID": message.author.id, "action": "throwCD"}) != None:
                    await message.channel.send(f"Please wait before using this command again")
                    return
                if message.content[6+len(prefix):] == '' or len(message.mentions) == 0:
                    await message.channel.send("You can't throw a snowball at nobody!")
                elif christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                    await message.channel.send(f"You dont have any snow balls to throw! \n(Do `{prefix}collect`)")
                elif christmasDB.find_one({"userID": message.author.id})["snowBalls"] == 0:
                    await message.channel.send(f"You dont have any snow balls to throw! \n(Do `{prefix}collect`)")
                else:
                    num = random.randint(0,1)
                    if num == 0:
                        balls = christmasDB.find_one({"userID": message.author.id})["snowBalls"]
                        balls = balls-1
                        misses = christmasDB.find_one({"userID": message.author.id})["misses"]
                        misses = misses+1
                        christmasDB.find_one_and_update({"userID": message.author.id}, {"$set":{"snowBalls": balls, "misses": misses}})
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
                        christmasDB.find_one_and_update({"userID": message.author.id}, {"$set":{"snowBalls": balls, "hits": hits}})
                        await message.channel.send(f"You wacked <@{message.mentions[0].id}> with a snowball! \nOuch!")
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"throwCD"})

            #stats command tree
            elif content[0] == prefix+"stats":
                if schedDB.find_one({"userID": message.author.id, "action": "statsCD"}) != None:
                    await message.channel.send(f"Please wait before using this command again")
                    return
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                user = christmasDB.find_one({"userID": message.author.id})
                await message.channel.send(f'__Your Snowy Stats__ \nSnowballs = {user["snowBalls"]}\nHits = {user["hits"]}\nTimes Hit = {user["timesHit"]}\nMisses = {user["misses"]}\nOverall Score = {(user["hits"]-user["timesHit"])}')
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 2, "action":"statsCD"})
                
            #leaderboard command tree
            elif content[0] == prefix+"leaderboard":
                if schedDB.find_one({"userID": message.author.id, "action": "chLeaderboardCD"}) != None:
                    await message.channel.send("Please wait before using this command again")
                    return
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                guild = client.get_guild(message.guild.id)
                embed = discord.Embed(title="__Server Leaderboard__", description="Top 10 snowball throwers in this server!", colour=0xFFFFFF)
                contenders = {}
                for doc in christmasDB.find():
                    if guild.get_member(int(doc["userID"])) is not None:
                        contenders[doc["userID"]] = (doc["hits"]-doc["timesHit"])
                contenders = {k: v for k, v in sorted(contenders.items(), key=lambda item: item[1])}
                contList = list(contenders.keys())
                contList2 = []
                if len(contList) < 10: num = len(contList)
                else: num = 10
                for i in range(0, num):
                    contList2.insert(i, contList[len(contList)-(i+1)])
                    user = christmasDB.find_one({"userID": contList[len(contList)-(i+1)]})
                    if i == 0:
                        embed.add_field(name=f'__**{str(i+1)}: user["userName"]**__', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                    else: embed.add_field(name=f'{str(i+1)}: user["userName"]', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                if not message.author.id in contList2:
                    authorIndex = contList.index(message.author.id)
                    user = christmasDB.find_one({"userID": message.author.id})
                    embed.add_field(name=f'**{authorIndex}: {message.author.name}**', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                embed.set_footer(text=f"Leaderboard for {message.guild.name} as of {datetime.datetime.now()}. This command has a 30 second cooldown due to server strain.")
                await message.channel.send(embed=embed)
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 30, "action":"chLeaderboardCD"})
                
            #gleaderboard command tree
            elif content[0] in [prefix+"gleaderboard", prefix+"globalleaderboard"]:
                if schedDB.find_one({"userID": message.author.id, "action": "chGLeaderboardCD"}) != None:
                    await message.channel.send("Please wait before using this command again")
                    return
                if christmasDB.find_one({"userID": message.author.id}) == None:
                    christmassy(message.author)
                guild = client.get_guild(message.guild.id)
                embed = discord.Embed(title="Global Leaderboard__", description="Top 10 snowball throwers in the world!", colour=0xFFFFFF)
                contenders = {}
                for doc in christmasDB.find():
                    contenders[doc["userID"]] = (doc["hits"]-doc["timesHit"])
                contenders = {k: v for k, v in sorted(contenders.items(), key=lambda item: item[1])}
                contList = list(contenders.keys())
                contList2 = []
                if len(contList) < 10: num = len(contList)
                else: num = 10
                for i in range(0, num):
                    contList2.insert(i, contList[len(contList)-(i+1)])
                    user = christmasDB.find_one({"userID": contList[len(contList)-(i+1)]})
                    if i == 0:
                        embed.add_field(name=f'__**{str(i+1)}: user["userName"]**__', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                    else: embed.add_field(name=f'{str(i+1)}: user["userName"]', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                if not message.author.id in contList2:
                    authorIndex = contList.index(message.author.id)
                    user = christmasDB.find_one({"userID": message.author.id})
                    embed.add_field(name=f'**{authorIndex}: {message.author.name}**', value=f'Hits: {user["hits"]}, Times Hit: {user["timesHit"]}, Score: {(user["hits"]-user["timesHit"])}', inline=False)
                embed.set_footer(text=f"Leaderboard for the world as of {datetime.datetime.now()}. This command has a 180 second cooldown due to server strain.")
                await message.channel.send(embed=embed)
                schedDB.insert_one({"userID": message.author.id,"timeLeft": 180, "action":"chGLeaderboardCD"})
                                    
                

#Reports new reactions
@client.event
async def on_reaction_add(reaction,user):   #Find out if it's possible to get the reactions messageID. Could do reaction roles
    if user != client.user:
        for doc in schedDB.find({"action": "reactionAdd"}):
            if user.id == doc["userID"]:
                schedDB.find_one_and_update({"userID": doc["userID"], "action2": doc["action2"]}, {"$set":{"emoji": reaction.emoji}})

#Reports deleted messages
@client.event
async def on_message_delete(message):
    if serverDB.find_one({"serverID": message.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botspamEnabled"] == False:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"] == "":
        return
    elif message.content == '':
            return
    else:
        channel = message.guild.get_channel(serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"])
        embed = discord.Embed(title = f'Message Deleted', description=f"By <@{message.author.id}> in <#{message.channel.id}>", colour = 0xFF0000)
        embed.set_author(name=message.author,  icon_url=message.author.avatar_url)
        embed.add_field(name="Deleted Message:", value=message.content)
        embed.set_footer(text=message.guild.name+' - '+str(message.channel))
        await channel.send(embed=embed)

#Reports edited messages
@client.event
async def on_message_edit(message, message2):
    if serverDB.find_one({"serverID": message.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botspamEnabled"] == False:
        return
    elif serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"] == "":
        return
    elif message.content == '' or message2.content == '':
            return
    else:
        channel = message.guild.get_channel(serverDB.find_one({"serverID": message.guild.id})["botSpamChannel"])
        embed = discord.Embed(title = f'Message Edited', url=message.jump_url, description=f"By <@{message.author.id}> in <#{message.channel.id}>", colour = 0xFF0000)
        embed.set_author(name=message.author,  icon_url=message.author.avatar_url)
        embed.add_field(name='Before: ', value=message.content, inline=False)
        embed.add_field(name='After: ', value=message2.content, inline=False)
        embed.set_footer(text=message.guild.name+' - '+str(message.channel))
        await channel.send(embed=embed)

#Called when the bot joins a server
@client.event
async def on_guild_join(guild):
    if serverDB.find_one({"serverID": guild.id}) == None:
        serverDB.insert_one({"serverID": message.guild.id,
                                "prefix": prefix,
                                "verificationRole": "",
                                "botSpamChannel": "",
                                "suggestionChannel": "",
                                "welcomeChannel": "",
                                "joinMessage": "",
                                "leaveMessage": "",
                                "muteRole": "",
                                "numColours": 0,
                                "botspamEnabled": False,
                                "welcomeEnabled": False,
                                "currency": "birbseed"})

#Called when the bot leaves a server
#@client.event
#async def on_guild_remove(guild):
#    if serverDB.find_one({"serverID": guild.id}) != None:
#        serverDB.find_one_and_delete({"serverID": guild.id})

#Called when a member joins a server
@client.event
async def on_member_join(member):
    if member.bot == True:
        return
    elif currencyDB.find_one({"userID": member.id}) == None and invDB.find_one({"userID": member.id}) == None:
        currencyDB.insert_one({"userID": member.id,
                                "levelXP": 0,
                                "birbSeed": 0,
                                "accountID": "",
                                "password": ""})
        doc = {"userID": member.id, "items": 0}
        for i in range(1,110):
            doc[str(i)] = 0
        invDB.insert_one(doc)
    elif currencyDB.find_one({"userID": member.id}) != None and invDB.find_one({"userID": member.id}) == None:
        doc = {"userID": member.id, "items": 0}
        for i in range(1,110):
            doc[str(i)] = 0
        invDB.insert_one(doc)
    elif currencyDB.find_one({"userID": member.id}) == None and invDB.find_one({"userID": member.id}) != None:
        currencyDB.insert_one({"userID": member.id,
                                "levelXP": 0,
                                "birbSeed": 0,
                                "accountID": "",
                                "password": ""})
    #Server specific join message
    if serverDB.find_one({"serverID": member.guild.id}) == None:
        return
    elif serverDB.find_one({"serverID": member.guild.id})["welcomeEnabled"] == False:
        return
    elif serverDB.find_one({"serverID": member.guild.id})["joinMessage"] == "":
        return
    elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == "":
        return
    else:
        message = serverDB.find_one({"serverID": member.guild.id})["joinMessage"]
        channel = member.guild.get_channel(serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"])
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
        elif serverDB.find_one({"serverID": member.guild.id})["welcomeEnabled"] == False:
            return
        elif serverDB.find_one({"serverID": member.guild.id})["leaveMessage"] == "":
            return
        elif serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"] == "":
            return
        else:
            message = serverDB.find_one({"serverID": member.guild.id})["leaveMessage"]
            channel = member.guild.get_channel(serverDB.find_one({"serverID": member.guild.id})["welcomeChannel"])
            await channel.send(message.replace("{user}", "<@"+str(member.id)+">"))



#Starup
client.run(token)
