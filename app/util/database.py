import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import json
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set. Please export your Atlas connection string.")
print('using Atlas db via MONGO_URI')
mongo_client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=7000,  # faster fail if blocked
)

db = mongo_client['yctcdb']
mongo_client.admin.command("ping")
print("MongoDB Atlas connection OK")
admins = db['admins']
calendar_collection = db["calendar_events"]
sessions = db['sessions']
def createNewCollection(DBName, CollectionName: str):
    if CollectionName in DBName.list_collection_names():
        return False
    DBName.create_collection(CollectionName)
    return True

def createNewDB(DBName: str):
    #if DBName.startswith('N24'):
        #return None
    db = mongo_client[DBName]
    db.create_collection("init")
    db.init.insert_one({"TEST":"TEST"})
    return db


def createNewN24(DBName:str, year:int):
    if not DBName.startswith('N24'):
        return None
    with open("util/session.json",'r') as f:
        data = json.load(f)
    session = int(DBName.split('N24'))
    data['sessions'].append([session,year])
    with open("util/session.json",'w') as f:
        json.dump(data,f,indent=2)
    db = mongo_client[DBName]
    db.create_collection("init")
    db.init.insert_one({"TEST":"TEST"})
    return db

