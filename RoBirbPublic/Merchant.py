import pymongo
import random
import time
import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient

print("rb.Merchant initialised")
mongoClient = MongoClient('Your MongoDB URL goes here')
db = mongoClient.RoBirbBot
currencyDB = db.currency
schedDB = db.schedRequests

print("rb.Merchant online")
while True:
    wait = random.randint(15,60)
    schedDB.insert_one({"userID": "rb.Merchant",
                        "action": "merchantSpawn",
                        "timeLeft": wait*60,
                        "bot": "rb.Merchant"})
    time.sleep(wait*60)
    if schedDB.find_one({"userID": "rb.Merchant"}) != None:
        schedDB.find_one_and_delete({"userID": "rb.Merchant"})
    if currencyDB.find_one({"userID": "merchant.sell"}) != None or currencyDB.find_one({"userID": "merchant.buy"}) != None:
        currencyDB.find_one_and_delete({"userID": "merchant.buy"})
        currencyDB.find_one_and_delete({"userID": "merchant.sell"})
        
    buy = {"userID": "merchant.buy"}
    sell = {"userID": "merchant.sell"}
    for i in range(1,23):
        num = random.randint(1,8)
        buy[str(i)] = num
    
    for i in range(1, 23):
        num = random.uniform((random.randint(1,8)/10),1)
        sell[str(i)] = num
        
    currencyDB.insert_one(buy)
    currencyDB.insert_one(sell)
    print(f"Merchant spawned   | {datetime.datetime.now()}")
    
    time.sleep(random.randint(10,20)*60)
    print(f"Merchant despawned | {datetime.datetime.now()}")
    currencyDB.find_one_and_delete({"userID": "merchant.buy"})
    currencyDB.find_one_and_delete({"userID": "merchant.sell"})  
