from pymongo import MongoClient
import json

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

def get_chunk(skip, limit):
    pipeline = [
        { "$project": {"_id":0, "leagues":1, "matches":1, "nick":1, "ranked_stats":1,"sum_id":1 } },
        { "$skip": skip },
        { "$limit": limit }
    ]
    query = db['summoners'].aggregate(pipeline)
    query = list(query)

    done = len(query) == 0

    return query, done

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
