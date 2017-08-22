from pymongo import MongoClient
from db.queries import *
import json

client = MongoClient()
db = client['RUBoosted']

def all_summoner_nicks():
    query = db['summoners'].aggregate(all_nicks)
    sums = query_to_list(query)

    return sums

def get_players():
    cursor = db['summoners'].aggregate(all_summoners, allowDiskUse=True)
    query = list(cursor)
    cursor.close()

    return query

# Fetches a summoner given his nick
def get_summoner_by_nick(nick):
    pipeline = all_summoner_nicks(nick)
    query = db['summoners'].aggregate(pipeline)
    sum = list(query)[0]

    instance = json.loads(json.dumps(sum))

    return instance

# Casts a mongo query object to a list
def query_to_list(query):
    my_list = list(query)
    my_list = [next(iter(x.values())) for x in my_list]
    return my_list
