import time
import json
import numpy as np
import pandas as pd
import os.path

from db import db_manager as dbm
from db import summoner as s

script_path = os.path.dirname(__file__)
filename = os.path.join(script_path, 'roles2.txt')
champ_roles = json.loads(open(filename, 'r').read())
all_roles = np.unique([role['role'] for role in champ_roles])
stats_names = ['weights', 'avg_kda', 'avg_dmg', 'avg_wr', 'var_kda', 'var_dmg', 'var_wr']

def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division]

    for placement in placements:
        if placement == None:
            placement = ""

    return placements

def role_by_champion_id(id):
    # Find champion's role
    role = ""
    for r in champ_roles:
        if int(r['key']) == id:
            role = r['role']

    return role

# Returns the following attributes:
# avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr,
# kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr
def stats_per_champ(ranked_stats):
    base_stats = ['weights', 'kdas', 'dmgs', 'win_rates']
    # Initialize stats dicts with empty lists
    stats = dict()
    for r in all_roles:
        stats[r] = dict()
        for stat in base_stats:
            stats[r][stat] = []

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

        role = role_by_champion_id(champ['id'])

        # Compute KDA
        if deaths == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths
        win_rate = wins / games_played

        # Push stats to their role's array
        stats[role]['weights'].append(games_played)
        stats[role]['kdas'].append(kda)
        stats[role]['dmgs'].append(dmg)
        stats[role]['win_rates'].append(win_rate)

    for r in all_roles:
        # Skips if user didn't play with any champions of that role
        if len(stats[r]['weights']) == 0:
            stats[r]['weights'] = 1
            stats[r]['kdas'] = 0
            stats[r]['dmgs'] = 0
            stats[r]['win_rates'] = 0

        stats[r]['avg_kda'] = np.average(stats[r]['kdas'], weights=stats[r]['weights'])
        stats[r]['avg_dmg'] = np.average(stats[r]['dmgs'], weights=stats[r]['weights'])
        stats[r]['avg_wr'] = np.average(stats[r]['win_rates'], weights=stats[r]['weights'])

        stats[r]['var_kda'] = np.average((stats[r]['kdas'] - stats[r]['avg_kda'])**2, weights=stats[r]['weights'])
        stats[r]['var_dmg'] = np.average((stats[r]['dmgs'] - stats[r]['avg_dmg'])**2, weights=stats[r]['weights'])
        stats[r]['var_wr'] = np.average((stats[r]['win_rates'] - stats[r]['avg_wr'])**2, weights=stats[r]['weights'])

        stats[r]['weights'] = np.sum(stats[r]['weights'])

    # Compute_features
    result = []
    for role in all_roles:
        for stat in stats_names:
            result.append(stats[role][stat])

    return result


def get_features_labels(summarizations, base_stats):
    labels = []
    for s in summarizations:
        for bs in base_stats:
            labels += s + "_" + bs
    return labels


def matches_details(matches):
    base_stats = ['goldEarned', 'totalDamageTaken', 'totalMinionsKilled', 'visionScore', 'visionWardsBoughtInGame',
                  'wardsKilled', 'wardsPlaced']
    summarizations = ['avg', 'var']

    features = get_features_labels(summarizations, base_stats)
    # TODO: CONTINUAR

    # Initialize stats dicts with empty lists
    stats = dict()
    for r in all_roles:
        stats[r] = dict()
        for stat in base_stats:
            stats[r][stat] = []

    for match in matches:
        role = role_by_champion_id(match['champion'])
        print('> ', match['champion'], role)
        print(match['participant']['stats']['goldEarned'])
        print(match['participant']['stats']['totalDamageTaken'])
        print(match['participant']['stats']['totalMinionsKilled'])
        print(match['participant']['stats']['visionScore'])
        print(match['participant']['stats']['visionWardsBoughtInGame'])
        print(match['participant']['stats']['wardsKilled'])
        print(match['participant']['stats']['wardsPlaced'])

def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]

# Combine roles and stats names to get labels
def get_labels():
    stats_labels = []
    for role in all_roles:
        for stat in stats_names:
            stats_labels.append(role+'_'+stat)

            # Trocar por !!!
            # get_features_labels()

    stats_labels = '\t'.join(stats_labels)
    labels = 'nick\tn_matches\t' + stats_labels + '\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n'

    return labels

# Fills statistics with average for players that do not play some role
def fill_missing_role_stats():
    df = pd.read_csv('datasetv3.txt', sep='\t', index_col=False)

    # PODE ESTAR INVERTIDO!!!
    weight_features = get_features_labels(all_roles, ['weights'])
    stats_features = get_features_labels(all_roles, stats_names)

    for w_feat in weight_features:
        # Computes players that plays or not those champ_roles
        role_not_played = df.loc[:,w_feat] == 1
        role_played = df.loc[:,w_feat] != 1

        # The average is weighted by how many games the player has played in that role
        weights = df.loc[role_played,w_feat]

        for s_feat in stats_features:
            feature_avg = np.average(df.loc[role_played,s_feat].as_matrix(), weights=weights)
            df.loc[role_not_played, s_feat] = feature_avg

    final = open('final2.txt', 'w', encoding="utf8")
    final.write(get_labels())

    for index, row in df.iterrows():
        for feature in row.as_matrix():
            final.write("%s\t" % feature)
        final.write("\n")

def dataset_v1():
    print('Building begun')

    ds = open('datasetv3.txt', "w", encoding="utf8")
    ds.write(get_labels())

    start_read_time = time.time()
    players = dbm.get_players()

    end_read_time = time.time()
    print('==================')
    print('Read total time: ', end_read_time-start_read_time)

    for i, sum in enumerate(players):
        # print("\t\t",start+i, sum['nick'])
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

    ds.close()
    fill_missing_role_stats()


def dataset_v2(skip=0):
    print('Building begun')

    if skip == 0:
        ds = open('DS.tsv', "w", encoding="utf8")
        ds.write(get_labels())
    else:
        ds = open('DS.tsv', "a", encoding="utf8")

    players = dbm.all_summoner_nicks(skip)

    for i, sum in enumerate(players):
        start_read_time = time.time()
        summoner_instance = s.Summoner(sum, cached=True, full=True)
        end_read_time = time.time()
        print('\t',skip+i, ':', sum,'\t\t', end_read_time-start_read_time)

        example = []

        # nick
        example += [summoner_instance.nick]
        # n_matches
        example += get_n_matches(summoner_instance)
        # stats
        example += stats_per_champ(summoner_instance.ranked_stats)
        # solo_q_tier, solo_q_division, flex_tier, flex_division
        example += tier_division(summoner_instance)
        #
        example += matches_details(summoner_instance.matches)

        for feature in example:
            ds.write("%s\t" % feature)

        ds.write("\n")

        dsa

    ds.close()
    fill_missing_role_stats()

# dataset_v1()
# fill_missing_role_stats()
dataset_v2(0)
