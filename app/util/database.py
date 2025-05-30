import os
from pymongo import MongoClient

docker_db = os.environ.get('DOCKER_DB', 'false')

if docker_db == 'true':
    print('using docker compose db')
    mongo_client = MongoClient('mongo')
else:
    print('using local db')
    mongo_client = MongoClient('localhost')

db = mongo_client['yctcdb']
admins = db['admins']
def createNewCollection(name: str):
    if name in db.list_collection_names():
        return False
    db.create_collection(name)
    return True
