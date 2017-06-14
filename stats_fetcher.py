import numpy as np
import time
import requests
import summoner as sum
import json
import os.path
import sys

class SummonerNotExists(Exception):
     def __init__(self, sum):
            self.value = "Summoner "+sum+ " does not exist."

     def __str__(self):
         return repr(self.value)


class SummonerNotCached(Exception):
    def __init__(self, sum):
        self.value = self.value = "Summoner "+sum+ " does not cached."

    def __str__(self):
        return repr(self.value)

class StatisticsFetcher():
    def __init__(self, dev_key="", verbose="False"):
        self.verbose = verbose

        if dev_key == "":
            self.dev_key = sys.argv[1]
        else:
            self.dev_key = dev_key

        self.responses = {
            'ranked_stats': {},
            'ids_by_nick': {},
            'matches': {},
            'leagues': {},
            'matches_details': {}
        }

    def ids_by_nick(self, nick):
        url = "https://br1.api.riotgames.com/lol/summoner/v3/summoners/by-name/"+nick+"?api_key="+self.dev_key
        headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": self.dev_key,
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        r = requests.get(url, headers=headers)
        self.responses['ids_by_nick'] = r

        # Summoner not found
        if 'status' in r.json() and r.json()['status']['status_code'] == 404:
            raise SummonerNotExists('Summoner not found')

        # Request failed
        if 'id' not in r.json() or 'accountId' not in r.json():
            raise Exception('id or accountId not in response')

        sum_id = r.json()['id']
        acc_id = r.json()['accountId']
        return sum_id, acc_id


    def ranked_stats(self, sum_id):
        url = "https://br.api.riotgames.com/api/lol/BR/v1.3/stats/by-summoner/"+str(sum_id)+"/ranked?season=SEASON2017&api_key="+self.dev_key
        headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": self.dev_key,
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        r = requests.get(url, headers=headers)
        self.responses['ranked_stats'] = r

        # Player does not play ranked games
        if 'status' in r.json() and r.json()['status']['status_code'] == 404:
            return []

        # Request failed
        if 'champions' not in r.json():
            raise Exception('champions not in response')

        stats = r.json()['champions']
        return stats


    def matches(self, acc_id):
        url = "https://br1.api.riotgames.com/lol/match/v3/matchlists/by-account/"+str(acc_id)+"?api_key="+self.dev_key
        headers = {
            "Origin": "https://developer.riotgames.com",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Riot-Token": self.dev_key,
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        r = requests.get(url, headers=headers)
        self.responses['matches'] = r

        # If request failed, repeat it
        if 'matches' not in r.json():
            raise Exception('matches not in response')

        matches = r.json()['matches']
        return matches


    def get_match(self, match_id):
        url = "https://br1.api.riotgames.com/lol/match/v3/matches/"+str(match_id)+"?api_key="+self.dev_key
        headers = {
            "Origin": "https://developer.riotgames.com",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36"
        }

        r = requests.get(url, headers=headers)
        self.responses['matches_full'] = r

        # If request failed, repeat it
        if r is not None and'status' in r.json() :
            raise Exception('\tMatch not successfully fetched. Trying again soon.')

        match = r.json()
        return match

    def cache_all_matches(self, start, end):
        summoners = sum.get_base_summoners()
        if end == -1: end = len(summoners)

        for i, summoner in enumerate(summoners[start:end]):
            # Computes de percentage of players completed
            perc = "%.2f" % ((start + i) / (len(summoners)-end))
            print("Summoner ", start + i, "/", len(summoners), "\t(" + perc + "%) : ",
                  summoner)

            try:
                s = sum.Summoner(summoner, cached=True)

            except SummonerNotExists:
                print('Summoner does not exist. Skipping.')
                continue

            except SummonerNotCached:
                print('Summoner not cached. Skipping.')
                continue

            except SummonerNotExists:
                print('Summoner does not exist. Skipping.')
                continue

            # For every S8 match that player played
            s8_matches, n_s8_matches = filter_s8_matches(s.matches)
            for j, match in enumerate(s8_matches):
                perc = "%.2f" % (j*100 / n_s8_matches)
                print("\t(",start+i,")\tMatch ", j, "/", n_s8_matches, "\t(" + perc + "%)")

                # Skips if match is already cached
                file_name = 'matches/' + str(match['gameId']) + '.txt'
                if os.path.isfile(file_name) == True:
                    print('\tSkipped')

                while True:
	                try:
	                	match_details = self.get_match(match['gameId'])
	                except Exception as e:
	                	print(e)
	                	time.sleep(30)
                	break

                # Write match to matches folder
                with open(file_name, 'w') as f:
                    content = json.dumps(match_details, default=lambda o: o.__dict__,
                                         sort_keys=True, indent=4)
                    f.write(content)




    def leagues(self, sum_id):
        url = "https://br1.api.riotgames.com/lol/league/v3/leagues/by-summoner/"+str(sum_id)+"?api_key="+self.dev_key
        headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": self.dev_key,
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        r = requests.get(url, headers=headers)

        if 'entries' not in r.json()[0]:
            raise Exception('entries not in response')

        self.responses['leagues'] = r

        return r.json()

    def fetch_all(self, nick):
        # Tries to find summoner
        try:
            sum_id, acc_id = self.ids_by_nick(nick)
            sum_id = sum_id
            acc_id = acc_id

            # Tries to fetch all statistics
            try:
                ranked_stats = self.ranked_stats(sum_id)
                matches = self.matches(acc_id)
                leagues = self.leagues(sum_id)
            except Exception as e:
                print(e, ". We'll wait a minute before trying again")
                if self.verbose:
                    self.log_responses()

                time.sleep(60)
                return self.fetch_all(nick)

        except SummonerNotExists as e:
            raise e
        except Exception as e:
            print(e, ". We'll wait a minute before trying again")
            if self.verbose == True:
                self.log_responses()


            time.sleep(60)
            return self.fetch_all(nick)

        if self.verbose:
            self.log_responses()
        return sum_id, acc_id, ranked_stats, matches, leagues


    def log_responses(self):
        for key, value in self.responses.items():
            print('\t',key, value)

    def cache_all_summoners(start=0):
        summoners = sum.get_base_summoners()

        for i, summoner in enumerate(summoners[start:]):
            # Computes de percentage of players completed
            perc = "%.2f" % ((start + i)*100 / len(summoners))
            print("Summoner ", start + i, "/", len(summoners), "\t(" + perc + "%) : ",
                  summoner)

            try:
                s = sum.Summoner(summoner)
            except SummonerNotExists:
                print('Summoner does not exist. Skipping.')
                continue
            if(s.acc_id is not None):
                s.serialize_summoner()

    def cache_summoner(k):
        summoners = sum.get_base_summoners()

        summoner = summoners[k]
        print("Summoner ", k, ": ", summoner)

        try:
            s = sum.Summoner(summoner)
        except SummonerNotExists:
            print('Summoner does not exist. Skipping.')

        if(s.acc_id is not None):
            s.serialize_summoner()


def filter_s8_matches(matches):
    def is_s8_match(match): return match['season'] == 8
    season8 = np.array([is_s8_match(match) for match in matches])
    all_matches = np.array(matches)
    return all_matches[season8], len(all_matches[season8])

