# Python Discord Bot
Public branch of RoBirbs code

This is a Discord bot that has everything from a currency system to the ability to punch your mate in the face. It's a prefix bot that requires administrator permissions and a connected MongoDB database.

RoBirb is the main project of mine, which I have spent countless hours on. So here, have the code so you won't need to spend countless hours as well!
It has everything from a currency system (as long as you link a MongoDB database), to an inventory system, to gambling games and moderation features.
I've removed the bot token and database URL (for obvious reasons). Feel free to add your own, and use this framework for your own bot.
This is currently updated to the latest version of the bot. However, this is no longer maintained as I have moved on to other things.


## How to use
First, download the files. Next, download Discord.py and PyMongo using Pip or the like. 
Next, make a Discord Application. A guide can be found [here](https://discordpy.readthedocs.io/en/stable/discord.html). Make sure that the invite has `administrator` permissions.
Next, open RoBirb_Test.py and set `token` to be your previously created application's token.
After that, you need to make a MongoDB database. You can use a different database provider, but you would need to edit the code for that. A guide can be found [here](https://www.mongodb.com/basics/create-database). Name the database whatever you like. Go into RoBirb_Test.py and make a collection (within the database) for everything under 'MongoDB Initialisation'.
For the rest of the steps, follow what it says within RoBirb_Test. You will also need to add the database connection string, and database name to the scheduler and merchant.
Now, run all three files. Assuming you've done everything correctly, and I've explained it clearly enough, you should now have a functional Discord bot.
If it doesn't work, however, feel free to send any queries to me: 'Chris22426#0001' on Discord. Or 'chris270305@icloud.com' through email.
