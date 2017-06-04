from stats_fetcher import *
import json

class Summoner:
    def __init__(self, nick):
        self.nick = nick

        sum_id, acc_id = ids_by_nick(nick)
        self.sum_id = sum_id
        self.acc_id = acc_id
        # self.ranked_stats = ranked_stats(self.sum_id)
        # self.matches = matches(self.acc_id)
        self.leagues = leagues(self.sum_id)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

    def serialize_summoner(self):
        with open(self.nick+'.txt', 'w') as outfile:
            outfile.write(self.toJSON())
