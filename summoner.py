import stats_fetcher as stf
import json
import time
from enum import Enum

class Elo(Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    DIAMOND = 4
    MASTER = 5
    CHALLENGER = 5

    def elos_list(limited=False):
        elos = []
        for elo in Elo:
            elos.append(elo.name)
            if limited:
                if elo.name == 'DIAMOND':
                    break

        return elos

class Summoner:
    def __init__(self, nick, cached=False, fill=True):
        if not cached:
            sf = stf.StatisticsFetcher()
            self.nick = nick

            try:
                sum_id, acc_id, ranked_stats, matches, leagues = sf.fetch_all(nick)

                self.sum_id = sum_id
                self.acc_id = acc_id
                self.ranked_stats = ranked_stats
                self.matches = matches
                self.leagues = leagues

            except stf.SummonerNotExists:
                raise stf.SummonerNotExists(nick)
        else:
            try:
                self.deserialize_summoner(nick, fill)
            except FileNotFoundError:
                raise stf.SummonerNotCached(nick)


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def serialize_summoner(self):
        with open('summoners/'+self.nick+'.txt', 'w') as outfile:
            outfile.write(self.toJSON())

    def deserialize_summoner(self, nick, fill=True):
        with open('summoners/' + nick + '.txt', 'r') as cache:
            content = cache.read()
        self.__dict__ = json.loads(content)

        if fill == True:
            self.fill_missing_props()

    def fill_missing_props(self):
        if hasattr(self, 'ranked_stats') == False:
            self.ranked_stats = stf.ranked_stats(self.sum_id)
        if hasattr(self, 'matches') == False:
            self.matches = stf.matches(self.acc_id)
        if hasattr(self, 'leagues') == False:
            self.leagues = stf.leagues(self.sum_id)

