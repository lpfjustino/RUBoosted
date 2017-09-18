import time
import json
import numpy as np
import pandas as pd
import os.path

from db import db_manager as dbm
from db import summoner as s

script_path = os.path.dirname(__file__)

# Parameters (REFACTOR!):
resource_path = script_path + "/" + "resources/"
roles_file = "roles/roles3"
pool_file = "pools/10_pool"
dataset_file = "DS"
postprocessed_dataset_file = "pp_DS"
full_base = True

roles_file_name = os.path.join(script_path, resource_path, roles_file + '.txt')
champ_roles = json.loads(open(roles_file_name, 'r').read())
all_roles = np.unique([role['role'] for role in champ_roles])

handle_stats = {
    'goldEarned': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'kills': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'deaths': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'assists': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'totalDamageTaken': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'totalMinionsKilled': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'visionScore': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'visionWardsBoughtInGame': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'gameDuration': {'reduce': 'disp', 'default': {'avg': 0, 'var': 0}},
    'won': {'reduce': 'sum', 'default': 0},
    'weight': {'reduce': 'sum', 'default': 1},
}
match_stats = list(handle_stats.keys())
summarizations = ['avg', 'var']


def tier_division(summoner_instance):
    placements = [summoner_instance.soloq_tier, summoner_instance.soloq_division, summoner_instance.flex_tier,
                  summoner_instance.flex_division]

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


def combine_into_labels(prefix, sufix):
    labels = []
    for p in prefix:
        for s in sufix:
            labels.append(p + "_" + s)
    return labels


def search(d, key, default=None):
    """Return a value corresponding to the specified key in the (possibly
    nested) dictionary d. If there is no item with that key, return
    default.
    """
    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                break
            elif k == key:
                return v
        else:
            stack.pop()
    return default


def matches_details(matches, threshold=1):
    # Initialize stats dicts with empty lists
    stats = dict()
    for r in all_roles:
        stats[r] = dict()
        for stat in match_stats:
            if handle_stats[stat]['reduce'] == "disp":
                stats[r][stat] = []
            else:
                stats[r][stat] = 0

    # Fetch info from all matches
    for match in matches:
        role = role_by_champion_id(match['champion'])
        for bs in match_stats:
            value = int(search(match['participant'], bs))

            if handle_stats[bs]['reduce'] == "disp":
                stats[role][bs].append(value)
            else:
                stats[role][bs] += value

    result = []
    for role in all_roles:
        for bs in match_stats:
            if handle_stats[bs]['reduce'] == "disp":
                if stats[role]['weight'] < threshold:
                    avg = handle_stats[bs]['default']['avg']
                    var = handle_stats[bs]['default']['var']
                else:
                    avg = np.average(stats[role][bs])
                    var = np.average((stats[role][bs] - avg)**2)

                result += [avg, var]

            else:
                result += [np.sum(stats[role][bs])]

    return result


def get_n_matches(summoner_instance):
    return [len(summoner_instance.matches)]


# New generic function to generate the dataset's header
def generate_header():
    labels = []

    for role in all_roles:
        for stat in match_stats:
            if handle_stats[stat]['reduce'] == 'disp':
                sum_stat = combine_into_labels(summarizations, [stat])
                role_stat = combine_into_labels([role], sum_stat)
                labels.append(role_stat)
            else:
                labels.append(combine_into_labels([role], [stat]))

    flattened = [val for sublist in labels for val in sublist]

    return flattened


# Combine roles and stats names to get labels
def get_labels():
    stats_labels = '\t'.join(generate_header())
    labels = 'nick\tn_matches\t' + stats_labels + '\tsolo_q_tier\tsolo_q_division\tflex_tier\tflex_division\n'

    return labels


# Fills statistics with average for players that do not play some role
def fill_missing_role_stats(threshold=1):
    df = pd.read_csv(resource_path + dataset_file + '.tsv', sep='\t', index_col=False)

    for role in all_roles:
        weight_feature = combine_into_labels([role], ['weight'])

        # Computes players that plays or not those champ_roles
        role_not_played = (df.loc[:,weight_feature] <= threshold).values.flatten()
        role_played = (df.loc[:,weight_feature] > threshold).values.flatten()

        # Only postprocess dispersion measure attributes
        to_be_postprocessed = [stat for stat in handle_stats if handle_stats[stat]['reduce'] == 'disp']

        stats_features = combine_into_labels([role], summarizations)
        stats_features = combine_into_labels(stats_features, to_be_postprocessed)

        # The average is weighted by how many games the player has played in that role
        weights = df.loc[role_played, weight_feature].values.flatten()

        for s_feat in stats_features:
            if len(weights) > 0:
                feature_avg = np.average(df.loc[role_played, s_feat].as_matrix(), weights=weights)
            else:
                feature_avg = 0

            # Replacing by average
            df.loc[role_not_played, s_feat] = feature_avg

    final = open(resource_path + "pp_" + dataset_file + '.tsv', 'w', encoding="utf8")

    # Copy header
    final.write("\t".join(list(df.columns.values)))
    final.write('\n')

    for index, row in df.iterrows():
        for feature in row.as_matrix():
            final.write("%s\t" % feature)
        final.write("\n")


# Removes examples with missing statistics
def remove_missing_role_stats(threshold=1):
    df = pd.read_csv(resource_path + dataset_file + '.tsv', sep='\t', index_col=False)

    weight_features = combine_into_labels(all_roles, ['weight'])
    role_not_played = ((df.loc[:, weight_features] <= threshold).transpose().any()).values.flatten()
    print('Removed:', role_not_played.sum(), '/', len(role_not_played))
    role_played = ((df.loc[:, weight_features] > threshold).transpose().all())

    df = df.loc[role_played, :]

    final = open(resource_path + postprocessed_dataset_file + '.tsv', 'w', encoding="utf8")

    # Copy header
    final.write("\t".join(list(df.columns.values)))
    final.write('\n')

    for index, row in df.iterrows():
        for feature in row.as_matrix():
            final.write("%s\t" % feature)
        final.write("\n")

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

    print('Players read')
    print('Base size:', len(players))

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

# dataset_v2(0)
# dataset_v2(869)
fill_missing_role_stats(threshold=1)
# remove_missing_role_stats()
