import time
import json
import numpy as np

from db import db_manager as dbm
from db import summoner as s

roles = json.loads(open('roles.txt', 'r').read())
all_roles = np.unique([role['role'] for role in roles])
stats_names = ['weights', 'avg_kda', 'avg_dmg', 'avg_wr', 'var_kda', 'var_dmg', 'var_wr',
             'kurt_kda', 'kurt_dmg', 'kurt_wr', 'skew_kda', 'skew_dmg', 'skew_wr']

def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division]

    for placement in placements:
        placement.replace("None","")

    return placements

def initialize_stats_dicts(all_roles):
    # Create empty dictionaries by role
    kdas = dict((role,[]) for role in all_roles)
    dmgs = dict((role,[]) for role in all_roles)
    win_rates = dict((role,[]) for role in all_roles)
    weights = dict((role,[]) for role in all_roles)

    avg_kda = dict((role, []) for role in all_roles)
    avg_dmg = dict((role, []) for role in all_roles)
    avg_wr = dict((role, []) for role in all_roles)
    var_kda = dict((role, []) for role in all_roles)
    var_dmg = dict((role, []) for role in all_roles)
    var_wr = dict((role, []) for role in all_roles)
    kurt_kda = dict((role, []) for role in all_roles)
    kurt_dmg = dict((role, []) for role in all_roles)
    kurt_wr = dict((role, []) for role in all_roles)
    skew_kda = dict((role, []) for role in all_roles)
    skew_dmg = dict((role, []) for role in all_roles)
    skew_wr = dict((role, []) for role in all_roles)

    return avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr, kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr, kdas,dmgs, win_rates, weights

def compute_fetures(stats, all_roles):
    result = []
    for role in all_roles:
        for stat in stats:
            result.append(stat[role])

    print (len(result))

    return result

def stats_per_champ(ranked_stats):
    avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr, kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr, \
        kdas, dmgs, win_rates, weights = initialize_stats_dicts(all_roles)

    for champ in ranked_stats:
        # Skips the anomalous id 0 champion
        if champ['id'] == 0:
            continue

        kills = champ['stats']['totalChampionKills']
        deaths = champ['stats']['totalDeathsPerSession']
        assists = champ['stats']['totalAssists']
        dmg = champ['stats']['totalDamageDealt']
        wins = champ['stats']['totalSessionsWon']
        games_played = champ['stats']['totalSessionsPlayed']

        # Find champion's role
        role = ""
        for r in roles:
            if int(r['key']) == champ['id']:
                role = r['role']

        # Compute KDA
        if deaths == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths
        win_rate = wins / games_played

        # Push stats to their role's array
        weights[role].append(games_played)
        kdas[role].append(kda)
        dmgs[role].append(dmg)
        win_rates[role].append(win_rate)

    for r in all_roles:
        # Skips if user didn't play with any champions of that role
        if len(weights[r]) == 0:
            weights[r].append(1)
            kdas[r].append(0)
            dmgs[r].append(0)
            win_rates[r].append(0)

        avg_kda[r] = np.average(kdas[r], weights=weights[r])
        avg_dmg[r] = np.average(dmgs[r], weights=weights[r])
        avg_wr[r] = np.average(win_rates[r], weights=weights[r])

        var_kda[r] = np.average((kdas[r] - avg_kda[r]) ** 2, weights=weights[r])
        var_dmg[r] = np.average((dmgs[r] - avg_dmg[r]) ** 2, weights=weights[r])
        var_wr[r] = np.average((win_rates[r] - avg_wr[r]) ** 2, weights=weights[r])

        kurt_kda[r] = np.average((kdas[r] - avg_kda[r]) ** 3, weights=weights[r])
        kurt_dmg[r] = np.average((dmgs[r] - avg_dmg[r]) ** 3, weights=weights[r])
        kurt_wr[r] = np.average((win_rates[r] - avg_wr[r]) ** 3, weights=weights[r])

        skew_kda[r] = np.average((kdas[r] - avg_kda[r]) ** 4, weights=weights[r])
        skew_dmg[r] = np.average((dmgs[r] - avg_dmg[r]) ** 4, weights=weights[r])
        skew_wr[r] = np.average((win_rates[r] - avg_wr[r]) ** 4, weights=weights[r])

        weights[r] = np.sum(weights[r])

    stats = [weights, avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr,
             kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr]

    return compute_fetures(stats, all_roles)

def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]

def get_labels():
    stats_labels = []
    for role in all_roles:
        for stat in stats_names:
            stats_labels.append(role+'_'+stat)

    stats_labels = '\t'.join(stats_labels)
    labels = 'nick\tn_matches\t' + stats_labels + '\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n'
    print(labels)
    return labels

def dataset_v1(start=0):
    print('Building begun')

    # Write header
    if start == 0:
        ds = open('dataset2.txt', "w", encoding="utf8")
        ds.write(get_labels())

    else:
        ds = open('_dataset2.txt', "a", encoding="utf8")


    start_read_time = time.time()
    players = dbm.get_players()

    end_read_time = time.time()
    print('==================')
    print('Read total time: ', end_read_time-start_read_time)

    for i, sum in enumerate(players):
        # print("\t\t",start+i, sum['nick'])
        # try:
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


        # except Exception as e:
        #     print(sum['nick'], 'failed.', e)


def dataset_v2():
    pass

dataset_v1()
