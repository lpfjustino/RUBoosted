import stats_fetcher as stf
import json
import time
from enum import Enum
import db_manager as dbm

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
    def __init__(self, nick, cached=False, fill=True, instance=None):
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
                if instance is None:
                    self.deserialize_by_nick(nick, fill)
                else:
                    self.deserialize_by_instance(instance)
            except FileNotFoundError:
                raise stf.SummonerNotCached(nick)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def serialize_summoner(self):
        with open('summoners/'+self.nick+'.txt', 'w') as outfile:
            outfile.write(self.toJSON())

    def deserialize_by_nick(self, nick, fill=True):
        self.__dict__ = dbm.get_summoner_by_nick(nick)

        if fill == True:
            self.fill_missing_props()

    def deserialize_by_instance(self, instance, fill=True):
        self.__dict__ = json.loads(json.dumps(instance))

        if fill == True:
            self.fill_missing_props()

    def fill_missing_props(self):
        if hasattr(self, 'ranked_stats') == False:
            self.ranked_stats = stf.ranked_stats(self.sum_id)
        if hasattr(self, 'matches') == False:
            self.matches = stf.matches(self.acc_id)
        if hasattr(self, 'leagues') == False:
            self.leagues = stf.leagues(self.sum_id)



