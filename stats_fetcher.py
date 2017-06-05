import numpy as np
import time
import requests
from summoner import Summoner, get_base_summoners

def ids_by_nick(nick, verbose=True):
    url = "https://br1.api.riotgames.com/lol/summoner/v3/summoners/by-name/"+nick+"?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    if verbose:
        print(r.json())

    # Summoner not found
    if 'status' in r.json() and r.json()['status']['status_code'] == 404:
        return None, None

    # If request failed, repeat it
    while 'id' not in r.json() or 'accountId' not in r.json():
        time.sleep(300)
        r = requests.get(url, headers=headers)

    sum_id = r.json()['id']
    acc_id = r.json()['accountId']
    return sum_id, acc_id


def ranked_stats(sum_id, verbose=True):
    url = "https://br.api.riotgames.com/api/lol/BR/v1.3/stats/by-summoner/"+str(sum_id)+"/ranked?season=SEASON2017&api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    if verbose:
        print(r.json())

    if 'status' in r.json() and r.json()['status']['status_code'] == 404:
        return []

    # If request failed, repeat it
    while 'champions' not in r.json():
        time.sleep(300)
        r = requests.get(url, headers=headers)

    stats = r.json()['champions']
    return stats


def matches(acc_id, verbose=True):
    url = "https://br1.api.riotgames.com/lol/match/v3/matchlists/by-account/"+str(acc_id)+"?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    if verbose:
        print(r.json())

    # If request failed, repeat it
    while 'matches' not in r.json():
        time.sleep(300)
        r = requests.get(url, headers=headers)

    matches = r.json()['matches']
    return matches


def leagues(sum_id, verbose=True):
    url = "https://br1.api.riotgames.com/lol/league/v3/leagues/by-summoner/"+str(sum_id)+"?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    if verbose:
        print(r.json())

    return r.json()


def cache_all_summoners(start=0):
    summoners = get_base_summoners()

    for i, summoner in enumerate(summoners[start:]):
        print("Summoner ", start + i, "/", len(summoners), "("+str((start+i)/len(summoners))+"%) : ", summoner)
        s = Summoner(summoner)
        if(s.acc_id is not None):
            s.serialize_summoner()

def filter_s8_matches(summoner):
    def is_s8_match(match): return match['season'] == 8
    season8 = [is_s8_match(match) for match in summoner.matches]
    all_matches = np.array(summoner.matches)
    return all_matches[season8]