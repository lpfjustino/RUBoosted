from pymongo import MongoClient

client = MongoClient()
db = client['RUBoosted']

def get_base_summoners():
    pipeline = [
        { "$project": {"_id":0, "nick":1} },
        { "$group": { "_id": "$nick" } }
    ]
    query = db['summoners'].aggregate(pipeline)

    sums = list(query)
    sums = [next(iter(x.values())) for x in sums]
    return sums