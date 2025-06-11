import os
from pymongo import MongoClient
import json

docker_db = os.environ.get('DOCKER_DB', 'false')

if docker_db == 'true':
    print('using docker compose db')
    mongo_client = MongoClient('mongo')
else:
    print('using local db')
    mongo_client = MongoClient('localhost')

db = mongo_client['yctcdb']

admins = db['admins']
calendar_collection = db["calendar_events"]
sessions = db['sessions']

def createNewCollection(DBName, CollectionName: str):
    if CollectionName in DBName.list_collection_names():
        return False
    DBName.create_collection(CollectionName)
    return True

def createNewDB(DBName: str):
    if DBName.startswith('N24'):
        return None
    db = mongo_client[DBName]
    db.create_collection("init")
    db.init.insert_one({"TEST":"TEST"})
    return db

def createNewDB(DBName:str, year:int):
    if not DBName.startswith('N24'):
        return None
    with open("util/sessions.json",'r') as f:
        data = json.load(f)
    session = int(DBName.split('N24'))
    data['sessions'].append([session,year])
    with open("util/session.json",'w') as f:
        json.dump(data,f,indent=2)
    db = mongo_client[DBName]
    db.create_collection("init")
    db.init.insert_one({"TEST":"TEST"})
    return db
