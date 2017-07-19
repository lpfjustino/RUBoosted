import time

import numpy as np

from db import db_manager as dbm
from db import summoner as s
from tools.stats_fetcher import filter_s8_matches


# def tier_division(summoner_instance):
#     solo_q_tier = summoner_instance.leagues[0]['tier']
#     solo_q = summoner_instance.leagues[0]['entries']
#     solo_q_division = [player for player in solo_q if player['playerOrTeamName'] == summoner_instance.nick][0]['rank']
#
#     flex_tier = ""
#     flex_division = ""
#
#     # Player plays solo queue and flex
#     plays_two_queues = len(summoner_instance.leagues) > 1
#     if plays_two_queues:
#         flex_tier = summoner_instance.leagues[1]['tier']
#         flex = summoner_instance.leagues[1]['entries']
#         flex_division = [player for player in flex if player['playerOrTeamName'] == summoner_instance.nick][0]['rank']
#
#     # Player only plays flex
#     if not plays_two_queues and summoner_instance.leagues[0]['queue'] == "RANKED_FLEX_SR":
#         flex_tier = solo_q_tier
#         flex_division = solo_q_division
#         solo_q_tier = ""
#         solo_q_division = ""
#
#     return solo_q_tier, solo_q_division, flex_tier, flex_division

def tier_division(summoner_instance):
    # return summoner_instance['solo_q_tier'], summoner_instance['solo_q_division'],\
    #        summoner_instance['flex_tier'], summoner_instance['flex_division']

    return summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division

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
    return avg_kda, avg_dmg, avg_wr

def get_n_matches(summoner_instance):
    return len(summoner_instance.matches)

def dataset_v1(start=0):
    print('Building begun')

    # Write header
    if start == 0:
        ds = open('dataset2.txt', "w", encoding="utf8")
        ds.write('nick\tn_matches\tkda\tdmg\twin_rate\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n')
    else:
        ds = open('dataset2.txt', "a", encoding="utf8")

    done = False
    current = 0
    pool = 6000
    # while not done:
    #     print("\tChunk", int(current / pool) + 1)

    start_read_time = time.time()
    players, done = dbm.get_chunk(current,pool)

    # current += pool

    end_read_time = time.time()
    print('==================')
    print('Read total time: ', end_read_time-start_read_time)

    for i, sum in enumerate(players):
        # print("\t\t",start+i, sum['nick'])
        try:
            summoner_instance = s.Summoner(sum['nick'], cached=True, instance=sum)

            solo_q_tier, solo_q_division, flex_tier, flex_division = tier_division(summoner_instance)
            # _, n_matches = filter_s8_matches(summoner_instance.matches)
            n_matches = get_n_matches(summoner_instance)

            kda, dmg, wr = stats_per_champ(summoner_instance.ranked_stats)

            nick = summoner_instance.nick
            ds.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (nick, n_matches, kda, dmg, wr, solo_q_tier, solo_q_division, flex_tier, flex_division))

        except Exception as e:
            print(sum['nick'], 'failed.', e)


def dataset_v2():
    pass

dataset_v1()
