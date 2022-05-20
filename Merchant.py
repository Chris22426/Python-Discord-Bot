import pymongo
import random
import time
import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
import FUNCTIONS

print("Merchant initialised")
mongoClient = MongoClient('')
db = mongoClient.doWhatYouWant
workDB = db.schedRequests
currencyDB = db.currency

print("Merchant online")
while True:
    wait = random.randint(15,60)*60
    workDB.insert_one({"userID": "Merchant",
                        "action": "merchantSpawn",
                        "timeLeft": wait,
                        "bot": "Merchant"})
    time.sleep(wait)
    if workDB.find_one({"userID": "Merchant"}) != None:
        workDB.find_one_and_delete({"userID": "Merchant"})
        
    test = {"userID": "Merchant"}
    for i in range(1,24):
        num = random.randint(1,8)
        test[str(i)] = num
    
    for i in range(24,47):
        num = random.uniform((random.randint(1,8)/10),1)
        test[str(i)] = num
        
    currencyDB.insert_one(test)
    print("Merchant spawned at   "+str(datetime.datetime.now()))
    
    time.sleep(random.randint(3,10)*60)
    print("Merchant despawned at "+str(datetime.datetime.now()))
    currencyDB.find_one_and_delete({"userID": "Merchant"})   