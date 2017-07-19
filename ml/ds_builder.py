import time

import numpy as np

from db import db_manager as dbm
from db import summoner as s

def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division]

    for placement in placements:
        placement.replace("None","")

    return placements

def stats_per_champ(ranked_stats):
    kdas = []
    dmgs = []
    win_rates = []
    weights = []

    for champ in ranked_stats:
        kills = champ['stats']['totalChampionKills']
        deaths = champ['stats']['totalDeathsPerSession']
        assists = champ['stats']['totalAssists']
        dmg = champ['stats']['totalDamageDealt']
        wins = champ['stats']['totalSessionsWon']
        games_played = champ['stats']['totalSessionsPlayed']

        if deaths == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths

        win_rate = wins / games_played

        weights.append(games_played)
        kdas.append(kda)
        dmgs.append(dmg)
        win_rates.append(win_rate)

    avg_kda = np.average(kdas, weights=weights)
    avg_dmg = np.average(dmgs, weights=weights)
    avg_wr = np.average(win_rates, weights=weights)

    var_kda = np.average((kdas - avg_kda) ** 2, weights=weights)
    var_dmg = np.average((dmgs - avg_dmg) ** 2, weights=weights)
    var_wr = np.average((win_rates - avg_wr) ** 2, weights=weights)

    kurt_kda = np.average((kdas - avg_kda) ** 3, weights=weights)
    kurt_dmg = np.average((dmgs - avg_dmg) ** 3, weights=weights)
    kurt_wr = np.average((win_rates - avg_wr) ** 3, weights=weights)

    skew_kda = np.average((kdas - avg_kda) ** 4, weights=weights)
    skew_dmg = np.average((dmgs - avg_dmg) ** 4, weights=weights)
    skew_wr = np.average((win_rates - avg_wr) ** 4, weights=weights)

    stats = [avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr,
             kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr]

    return stats

def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]

def dataset_v1(start=0):
    print('Building begun')

    # Write header
    if start == 0:
        ds = open('dataset2.txt', "w", encoding="utf8")
        ds.write('nick\tn_matches\tkda\tdmg\twin_rate\tvar_kda\tvar_dmg\tvar_wr\tkurt_kda\tkurt_dmg\tkurt_wr\t'+
                 'skew_kda\tskew_dmg\tskew_wr\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n')

    else:
        ds = open('dataset2.txt', "a", encoding="utf8")

    done = False

    start_read_time = time.time()
    players, done = dbm.get_players()

    end_read_time = time.time()
    print('==================')
    print('Read total time: ', end_read_time-start_read_time)

    for i, sum in enumerate(players):
        # print("\t\t",start+i, sum['nick'])
        try:
            summoner_instance = s.Summoner(sum['nick'], cached=True, instance=sum)
            example = []

            # nick
            example += [summoner_instance.nick]

            # n_matches
            example += get_n_matches(summoner_instance)

            # avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr,
            # kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr
            example += stats_per_champ(summoner_instance.ranked_stats)

            # solo_q_tier, solo_q_division, flex_tier, flex_division
            example += tier_division(summoner_instance)

            for feature in example:
                ds.write("%s\t" % feature)

            ds.write("\n")


        except Exception as e:
            print(sum['nick'], 'failed.', e)


def dataset_v2():
    pass

# dataset_v1()
