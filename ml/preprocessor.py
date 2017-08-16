import numpy as np
import pandas as pd

from db.summoner import Elo

from sklearn import preprocessing


def elo_to_enum(elo):
    return Elo[elo].value

def fill_queues(placements):
    no_solo_q = placements.loc[:,'solo_q_tier':'solo_q_division'].isnull().any(axis = 1)
    p_no_solo_q = placements.loc[no_solo_q]

    for i in p_no_solo_q.index.tolist():
        placements.iloc[i, 0] =  placements.iloc[i,2]
        placements.iloc[i, 1] =  placements.iloc[i,3]

    no_flex = placements.loc[:,'flex_tier':'flex_division'].isnull().any(axis = 1)
    p_no_flex = placements.loc[no_flex]

    for i in p_no_flex.index.tolist():
        placements.iloc[i, 2] =  placements.iloc[i,0]
        placements.iloc[i, 3] =  placements.iloc[i,1]


def set_elos(placements):
    fill_queues(placements)

    # print(placements)

    elos = placements.iloc[:,0].apply(elo_to_enum)
    placements.iloc[:,0] = elos
    elos = placements.iloc[:,2].apply(elo_to_enum)
    placements.iloc[:,2] = elos


def uniform_elo_sampling(data):
    samples = []
    uniform = pd.DataFrame()
    smallest_pool = float('inf')

    for elo in Elo:
        is_such_elo = data.loc[:,'solo_q_tier'] == elo.value
        players = data[is_such_elo]
        samples.append(players)

        if len(players) < smallest_pool:
            smallest_pool = len(players)

        # Ignoring masters and challengers
        if elo.value == Elo['DIAMOND'].value:
            break

    # smallest_pool = 500
    for sample in samples:
        uniform = uniform.append(sample.iloc[:smallest_pool, :])

    return uniform, smallest_pool

def rescale(data):
    data -= np.mean(data, axis=0)
    data /= np.std(data, axis=0)

    print(data.mean(axis=0))
    print(data.std(axis=0))
    dsa

    return data


def preprocess(my_df, n_labels, features, chosen_features):
    df = my_df.copy()

    # Translate elos to numbers
    placements = df.loc[:, features[-n_labels:]] # The last 4 features are tiers and divisions
    set_elos(placements)
    df.loc[:, features[-n_labels:]] = placements

    #df, n = uniform_elo_sampling(df)

    df = df.loc[:, chosen_features]

    data_set = df.as_matrix().astype(float)
    # data_set = rescale(data_set)
    # print(data_set)
    rescaled_data_set = preprocessing.scale(data_set[:,:-1])

    # Concatenates the classes column and the rescaled dataset
    data_set = np.column_stack((rescaled_data_set, data_set[:,-1:]))

    return data_set, df









