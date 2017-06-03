import numpy as np

def fetch_all(summoners_list):
    base = []
    for summoner in summoners_list:
        base.append(summoner.nick)

        for i, queue in enumerate(summoner.leagues):
            players_in_league = summoner.leagues[i]['entries']

            for player in players_in_league:
                base.append(player['playerOrTeamName'])

    base = list(np.unique(base))
    return(base)