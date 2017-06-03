import requests

def ids_by_nick(nick):
    url = "https://br1.api.riotgames.com/lol/summoner/v3/summoners/by-name/luispfj?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers);
    sum_id = r.json()['id']
    acc_id = r.json()['accountId']
    return sum_id, acc_id


def ranked_stats(sum_id):
    url = "https://br.api.riotgames.com/api/lol/BR/v1.3/stats/by-summoner/"+str(sum_id)+"/ranked?season=SEASON2017&api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers);
    stats = r.json()['champions']
    return stats


def matches(acc_id):
    url = "https://br1.api.riotgames.com/lol/match/v3/matchlists/by-account/"+str(acc_id)+"?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers);
    matches = r.json()['matches']
    return matches


def leagues(sum_id):
    url = "https://br1.api.riotgames.com/lol/league/v3/leagues/by-summoner/"+str(sum_id)+"?api_key=RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d"
    headers = {
    "Origin": "https://developer.riotgames.com",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": "RGAPI-b3a0e588-5085-43cc-8778-bb2394a4541d",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    r = requests.get(url, headers=headers);
    leagues = r.json()
    return leagues