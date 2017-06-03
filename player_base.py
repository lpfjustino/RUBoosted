import numpy as np

import stats_fetcher
from summoner import Summoner

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


def build_player_base():
    summoner_names = ["Luispfj","Kail","Joxer","Soul Oblivious","Tomate Ervilha","Lyanhelios","TunderB","LionPrey","Sr genau","JuviaSutcliff","ReichsKanzler","Sickhazardinho","JessicaPS","enemysama","Yasu","Jiripo","Jarvan","Sereia Bjork","Saph1ra","Major Octavius","Princesa Lesgou","Moonsfury","l Lady Gaga l","Bidu de la Rocha","Prince Miles","peterp4nda","Portavoz92","GibaNelesXD","CólicaDeDeus","Foca II","Galinha Rafinha","MSouza01","SoulKanon ","Enleanor","toni mesmo","Vendo Bolo","lucasl42","torresgui","uema","XdextroierX","RunningSimulator","Fabricio201","ALGUEM ME MATE ","R2D2","RbRoDrIgO","RaposaVikingppppp"]
    summoners = []
    base = []
    for i,name in enumerate(summoner_names):
        print('Creating summoner ', i, ': ', name)
        summoner = Summoner(name)
        print('Done')
        print(i+1,'/',len(summoner_names))
        summoners.append(summoner)
        base += fetch_all(summoners)

    return base, summoners