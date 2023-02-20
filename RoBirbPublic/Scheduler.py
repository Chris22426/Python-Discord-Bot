import time
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient

mongoClient = MongoClient('Your MongoDB URL goes here')
db = mongoClient.YourDatabaseName
schedDB = db.schedRequests

print("Local Scheduler Online")
while True:
    if schedDB.find({}) != None:
        for x in schedDB.find():
            ID = x["_id"]
            if schedDB.find_one({"_id": ObjectId(str(ID))}) != None:
                timeLeft = schedDB.find_one({"_id": ObjectId(str(ID))})["timeLeft"]
                timeLeft = timeLeft - 1
                schedDB.find_one_and_update({"_id": ObjectId(str(ID))}, {"$set":{"timeLeft": timeLeft}})

    time.sleep(1)
    
    
    
# This is in no way, shape or form the best way to do this. I know this for a fact and have implimented a new way of doing this on the new Discord bot.
# This new system uses unix time codes instead of a counter, so this file is completely unnecessary.
# This system drifts roughly 13 minuets out over the course of a day. The new system has no drift at all. This file also crashes seemingly randomly, which is bad.
# Eventually, I will port this new system over to this bot. But, as of right now, I am focusing on getting the new bot up to scratch with this one.
