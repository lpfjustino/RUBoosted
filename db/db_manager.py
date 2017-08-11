import json

from pymongo import MongoClient

from db.queries import *

client = MongoClient()
db = client['RUBoosted']

def all_summoner_nicks():
    pipeline = [
        { "$project": {"_id":0, "nick":1} },
        { "$group": { "_id": "$nick" } }
    ]
    query = db['summoners'].aggregate(pipeline)
    sums = query_to_list(query)

    return sums

def get_players():
    cursor = db['summoners'].aggregate(summoners_pipeline, allowDiskUse=True)
    query = list(cursor)
    cursor.close()

    return query

def get_summoner_by_nick(nick):
    pipeline = [
        { "$match": { "nick":nick } },
        { "$project": {"_id": 0 } },
    ]
    query = db['summoners'].aggregate(pipeline)
    sum = list(query)[0]

    instance = json.loads(json.dumps(sum))

    return instance

def query_to_list(query):
    my_list = list(query)
    my_list = [next(iter(x.values())) for x in my_list]
    return my_list
