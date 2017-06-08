import summoner as s
import time
import numpy as np

def filter_s8_matches(matches):
    def is_s8_match(match): return match['season'] == 8
    season8 = [is_s8_match(match) for match in matches]
    all_matches = np.array(matches)
    return all_matches[season8], len(all_matches[season8])

def tier_division(summoner_instance):
    solo_q_tier = summoner_instance.leagues[0]['tier']
    solo_q = summoner_instance.leagues[0]['entries']
    solo_q_division = [player for player in solo_q if player['playerOrTeamName'] == summoner_instance.nick][0]['rank']

    flex_tier = ""
    flex_division = ""

    # Player plays solo queue and flex
    plays_two_queues = len(summoner_instance.leagues) > 1
    if plays_two_queues:
        flex_tier = summoner_instance.leagues[1]['tier']
        flex = summoner_instance.leagues[1]['entries']
        flex_division = [player for player in flex if player['playerOrTeamName'] == summoner_instance.nick][0]['rank']

    # Player only plays flex
    if not plays_two_queues and summoner_instance.leagues[0]['queue'] == "RANKED_FLEX_SR":
        flex_tier = solo_q_tier
        flex_division = solo_q_division
        solo_q_tier = ""
        solo_q_division = ""

    return solo_q_tier, solo_q_division, flex_tier, flex_division

def w_mean_kda(ranked_stats):
    kdas = []
    weights = []

    for champ in ranked_stats:
        kills = champ['stats']['totalChampionKills']
        deaths = champ['stats']['totalDeathsPerSession']
        assists = champ['stats']['totalAssists']
        games_played = champ['stats']['totalSessionsPlayed']

        if deaths == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths

        kdas.append(kda)
        weights.append(games_played)

    avg = np.average(kdas, weights=weights)
    return avg

def dataset_v1():
    base = s.get_base_summoners()
    print('Building begun')
    start_read_time = time.time()
    ds = open('dataset.txt', "w", encoding="utf8")
    ds.write('id\tnick\tn_matches\tsolo_q_tier\tsoloq_division\tflex_tier\tflex_division\n')

    for i, sum in enumerate(base[1:100]):
        try:
            f = open('summoners/' + sum + '.txt', encoding="utf8")
        except Exception as e:
            print(sum, 'failed.', e)
            continue

        summoner_instance = s.Summoner(sum, cached=True, fill=False)

        solo_q_tier, solo_q_division, flex_tier, flex_division = tier_division(summoner_instance)
        _, n_matches = filter_s8_matches(summoner_instance.matches)
        kda = w_mean_kda(summoner_instance.ranked_stats)

        id = i
        nick = summoner_instance.nick
        time.sleep(10)

        ds.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (id, nick, n_matches, solo_q_tier, solo_q_division, flex_tier, flex_division))


    end_read_time = time.time()

    print('==================')
    print('Read total time: ', end_read_time-start_read_time)