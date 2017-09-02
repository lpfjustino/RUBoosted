from pymongo import MongoClient
from db.queries import *
import json

client = MongoClient()
db = client['RUBoosted']

def all_summoner_nicks(skip=0):
    query = db['summoners'].aggregate(all_nicks(skip))
    sums = query_to_list(query)

    return sums

def get_players():
    cursor = db['summoners'].aggregate(all_summoners, allowDiskUse=True)
    query = list(cursor)
    cursor.close()

    return query

# Fetches a summoner given his nick
def get_summoner_by_nick(nick, join = False):
    pipeline = summoner_by_nick(nick)
    if join:
        pipeline = all_joined_summoners(nick)

    query = db['summoners'].aggregate(pipeline)
    sum = list(query)

    if len(sum) > 0:
        sum = sum[0]
        instance = json.loads(json.dumps(sum))

    else:
        raise Exception("Couldn't fetch summoner (likely join failed)")

    return instance

# Casts a mongo query object to a list
def query_to_list(query):
    my_list = list(query)
    my_list = [next(iter(x.values())) for x in my_list]
    return my_list

# import pprint as pp
# pp.pprint(get_summoner_by_nick('Luispfj', join=True))