import time
import json
import numpy as np
import pandas as pd
import os.path

from db import db_manager as dbm
from db import summoner as s

# Parameters (REFACTOR!):
resource_path = "resources/"
roles_file = "roles/roles"
pool_file = "pools/250_pool"
dataset_file = "DS"
full_base = False

script_path = os.path.dirname(__file__)
filename = os.path.join(script_path, resource_path, roles_file + '.txt')
champ_roles = json.loads(open(filename, 'r').read())
all_roles = np.unique([role['role'] for role in champ_roles])

champion_stats = ['kda', 'dmg', 'wr']
match_stats = ['goldEarned', 'totalDamageTaken', 'totalMinionsKilled', 'visionScore', 'visionWardsBoughtInGame']
all_stats = champion_stats + match_stats
summarizations = ['avg', 'var']

def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, \
           summoner_instance.flex_tier, summoner_instance.flex_division]

    for i, placement in enumerate(placements):
        if placement == None:
            placements[i] = ""

    return placements

def role_by_champion_id(id):
    # Find champion's role
    role = ""
    for r in champ_roles:
        if int(r['key']) == id:
            role = r['role']

    return role

# Returns the following attributes:
def stats_per_champ(ranked_stats, threshold = 1):
    base_stats = ['weights', 'kdas', 'dmgs', 'win_rates']
    stats_names = combine_into_labels(summarizations, champion_stats)

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
        # Skips if user didn't play enough matches with any champions of that role
        if len(stats[r]['weights']) < threshold:
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

    # Appends the weights and statistics for every role
    for role in all_roles:
        for stat in stats_names:
            result.append(stats[role][stat])
        result.append(stats[role]['weights'])

    return result


def combine_into_labels(prefix, sufix):
    labels = []
    for p in prefix:
        for s in sufix:
            labels.append(p + "_" + s)
    return labels


def matches_details(matches, threshold = 1):
    # Initialize stats dicts with empty lists
    stats = dict()
    for r in all_roles:
        stats[r] = dict()
        for stat in match_stats:
            stats[r][stat] = []

    # Fetch info from all matches
    for match in matches:
        role = role_by_champion_id(match['champion'])
        for bs in match_stats:
            stats[role][bs].append(match['participant']['stats'][bs])

    result = []
    for role in all_roles:
        for bs in match_stats:
            if len(stats[role][bs]) < threshold:
                avg = 0
                var = 0
            else:
                avg = np.average(stats[role][bs])
                var = np.average((stats[role][bs] - avg)**2)

            result += [avg, var]
    return result

def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]

# Auxiliary function to include weights
def get_labels_with_weights():
    stats_labels = []
    stat_champ = combine_into_labels(summarizations, champion_stats)
    for role in all_roles:
        role_stat_champ = combine_into_labels([role], stat_champ)
        stats_labels.append(role_stat_champ)
        # Adding weights statistic
        weight_stat = combine_into_labels([role],['weights'])
        stats_labels.append(weight_stat)
        flattened = [val for sublist in stats_labels for val in sublist]
    return flattened

# Combine roles and stats names to get labels
def get_labels(version='v2'):
    stats_labels = []

    labels = get_labels_with_weights()

    # Champion stats labels
    stats_labels += labels

    if version == 'v2':
        stat_match = combine_into_labels(summarizations, match_stats)
        role_stat_match = combine_into_labels(all_roles, stat_match)

        # Matches stats labels
        stats_labels += role_stat_match


    stats_labels = '\t'.join(stats_labels)
    labels = 'nick\tn_matches\t' + stats_labels + '\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n'

    return labels

# Fills statistics with average for players that do not play some role
def fill_missing_role_stats(threshold = 1):
    df = pd.read_csv(resource_path + dataset_file + '.tsv', sep='\t', index_col=False)


    for role in all_roles:
        weight_feature = combine_into_labels([role], ['weights'])

        # Computes players that plays or not those champ_roles
        role_not_played = (df.loc[:,weight_feature] <= threshold).values.flatten()
        role_played = (df.loc[:,weight_feature] > threshold).values.flatten()

        stats_features = combine_into_labels([role], summarizations)
        stats_features = combine_into_labels(stats_features, all_stats)

        # The average is weighted by how many games the player has played in that role
        weights = df.loc[role_played,weight_feature].values.flatten()

        for s_feat in stats_features:
            feature_avg = np.average(df.loc[role_played,s_feat].as_matrix(), weights=weights)
            df.loc[role_not_played, s_feat] = feature_avg

        # Leaves 1 as number of matches played
        df.loc[role_not_played, weight_feature] = 1

    final = open(resource_path + "pp_" + dataset_file + '.tsv', 'w', encoding="utf8")

    # Copy header
    final.write("\t".join(list(df.columns.values)))

    for index, row in df.iterrows():
        for feature in row.as_matrix():
            final.write("%s\t" % feature)
        final.write("\n")

def dataset_v1():
    print('Building begun')

    ds = open(resource_path + dataset_file + '.tsv', "w", encoding="utf8")
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
    failed = []
    print('Building begun')

    if skip == 0:
        ds = open(resource_path + dataset_file + '.tsv', "w", encoding="utf8")
        ds.write(get_labels())
    else:
        ds = open(resource_path + dataset_file + '.tsv', "a", encoding="utf8")

    if full_base:
        players = dbm.all_summoner_nicks(skip)
    else:
        f = open(resource_path + pool_file + '.txt')
        players = [x.replace('\n', '') for x in f.readlines()]

    for i, sum in enumerate(players):
        start_read_time = time.time()
        try:
            summoner_instance = s.Summoner(sum, cached=True, full=True)
        except Exception:
            failed.append(sum)
            continue

        end_read_time = time.time()
        print('\t',(skip+i)/len(players)*100, ':', sum,'\t\t', end_read_time-start_read_time)

        example = []

        # nick
        example += [summoner_instance.nick]
        # n_matches
        example += get_n_matches(summoner_instance)
        # champion stats
        example += stats_per_champ(summoner_instance.ranked_stats)
        # match stats
        example += matches_details(summoner_instance.matches)
        # solo_q_tier, solo_q_division, flex_tier, flex_division
        example += tier_division(summoner_instance)

        for feature in example:
            ds.write("%s\t" % feature)

        ds.write("\n")

    ds.close()
    print("The following summoners failed: ", failed)
    fill_missing_role_stats()

# dataset_v1()
dataset_v2(0)
# fill_missing_role_stats()
