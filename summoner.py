import stats_fetcher as sf
import json
import time

class Summoner:
    def __init__(self, nick, cached=False, fill=True, verbose=False):
        if not cached:
            self.nick = nick
            sum_id, acc_id = sf.ids_by_nick(nick, verbose=verbose)
            self.sum_id = sum_id
            self.acc_id = acc_id
            self.ranked_stats = sf.ranked_stats(self.sum_id, verbose=verbose)
            self.matches = sf.matches(self.acc_id, verbose=verbose)
            self.leagues = sf.leagues(self.sum_id, verbose=verbose)
        else:
            self.deserialize_summoner(nick, fill)


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
            self.ranked_stats = sf.ranked_stats(self.sum_id)
        if hasattr(self, 'matches') == False:
            self.matches = sf.matches(self.acc_id)
        if hasattr(self, 'leagues') == False:
            self.leagues = sf.leagues(self.sum_id)


def get_base_summoners():
    with open('base.txt', encoding="utf8") as f:
        content = f.readlines()[0]
        summoners = str.split(content, ',')

    return summoners

def get_cached_summoners_instances():
    # Instantiate every summoner name in base from cache
    base = get_base_summoners()
    summoner_instances = []
    for sum in base:
        try:
            with open('summoners/'+sum+'.txt', encoding="utf8") as f:
                summoner_instance = Summoner(sum, cached=True, fill=False)
                summoner_instances.append(summoner_instance)
        except:
            # print(sum, ' is not cached yet.')
            continue


    return summoner_instances
