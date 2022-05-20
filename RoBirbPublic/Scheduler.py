import time
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient

mongoClient = MongoClient('')
db = mongoClient.doWhateverYouWant
workDB = db.schedRequests
#num = 0

print("Scheduler Online")
while True:
    if workDB.find({}, {"userID":0,"channel":0,"guild":0,"action":0, "timeLeft":0, "bot":0}) == None or workDB.find({}, {"userID":0,"channel":0,"guild":0,"action":0, "timeLeft":0, "bot":0}) == 0:
        print('None')
    else:
        for x in workDB.find({}, {"userID":0,"channel":0,"guild":0,"action":0, "timeLeft":0, "bot":0}):
            ID = str(x)[18:42]
            if workDB.find_one({"_id": ObjectId(str(ID))}) != None:
                timeLeft = workDB.find_one({"_id": ObjectId(str(ID))})["timeLeft"]
                print(timeLeft)
                if timeLeft <= 0:
                    workDB.find_one_and_delete({"_id": ObjectId(str(ID))})
                else:
                    timeLeft = timeLeft - 1
                    workDB.find_one_and_update({"_id": ObjectId(str(ID))}, {"$set":{"timeLeft": timeLeft}})

    #num += 1
    time.sleep(1)
    