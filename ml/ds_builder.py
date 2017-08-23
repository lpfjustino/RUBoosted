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
base_stats = ['weights', 'kdas', 'dmgs', 'win_rates']
stats_names = ['weights', 'avg_kda', 'avg_dmg', 'avg_wr', 'var_kda', 'var_dmg', 'var_wr',
             'kurt_kda', 'kurt_dmg', 'kurt_wr', 'skew_kda', 'skew_dmg', 'skew_wr']

def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division]

    for placement in placements:
        if placement == None:
            placement = ""

    return placements

# Returns the following attributes:
# avg_kda, avg_dmg, avg_wr, var_kda, var_dmg, var_wr,
# kurt_kda, kurt_dmg, kurt_wr, skew_kda, skew_dmg, skew_wr
def stats_per_champ(ranked_stats):
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

        # Find champion's role
        role = ""
        for r in champ_roles:
            if int(r['key']) == champ['id']:
                role = r['role']

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

        stats[r]['var_kda'] = np.average((stats[r]['avg_kda'] - stats[r]['kdas']), weights=stats[r]['weights'])
        stats[r]['var_dmg'] = np.average((stats[r]['avg_dmg'] - stats[r]['dmgs']), weights=stats[r]['weights'])
        stats[r]['var_wr'] = np.average((stats[r]['avg_wr'] - stats[r]['win_rates']), weights=stats[r]['weights'])

        stats[r]['kurt_kda'] = np.average((stats[r]['kdas'] - stats[r]['avg_kda']) ** 3, weights=stats[r]['weights'])
        stats[r]['kurt_dmg'] = np.average((stats[r]['dmgs'] - stats[r]['avg_dmg']) ** 3, weights=stats[r]['weights'])
        stats[r]['kurt_wr'] = np.average((stats[r]['win_rates'] - stats[r]['avg_wr']) ** 3, weights=stats[r]['weights'])

        stats[r]['skew_kda'] = np.average((stats[r]['kdas'] - stats[r]['avg_kda']) ** 4, weights=stats[r]['weights'])
        stats[r]['skew_dmg'] = np.average((stats[r]['dmgs'] - stats[r]['avg_dmg']) ** 4, weights=stats[r]['weights'])
        stats[r]['skew_wr'] = np.average((stats[r]['win_rates'] - stats[r]['avg_wr']) ** 4, weights=stats[r]['weights'])

        stats[r]['weights'] = np.sum(stats[r]['weights'])

    print(stats)
    # Compute_features
    result = []
    for role in all_roles:
        for stat in stats_names:
            result.append(stats[role][stat])

    return result

def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]

def get_labels():
    stats_labels = []
    for role in all_roles:
        for stat in stats_names:
            stats_labels.append(role+'_'+stat)

    stats_labels = '\t'.join(stats_labels)
    labels = 'nick\tn_matches\t' + stats_labels + '\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n'

    return labels

def feature_labels(champ_roles, stats):
    feat = []
    for role in champ_roles:
        for stat in stats:
            feat.append(role + '_' + stat)

    return feat

def fill_missing_role_stats():
    df = pd.read_csv('datasetv3.txt', sep='\t', index_col=False)
    features = list(df)

    stats_names = ['weights']
    weight_features = feature_labels(all_roles, stats_names)
    stats_names = ['avg_kda', 'avg_dmg', 'avg_wr', 'var_kda', 'var_dmg', 'var_wr',
             'kurt_kda', 'kurt_dmg', 'kurt_wr', 'skew_kda', 'skew_dmg', 'skew_wr']
    stats_features = feature_labels(all_roles, stats_names)

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
        ds = open('DS.txt', "w", encoding="utf8")
        ds.write(get_labels())
    else:
        ds = open('DS.txt', "a", encoding="utf8")

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


        example += stats_per_champ(summoner_instance.ranked_stats)

        # solo_q_tier, solo_q_division, flex_tier, flex_division
        example += tier_division(summoner_instance)

        for feature in example:
            ds.write("%s\t" % feature)

        ds.write("\n")

    ds.close()
    fill_missing_role_stats()

# dataset_v1()
# fill_missing_role_stats()
dataset_v2(0)
