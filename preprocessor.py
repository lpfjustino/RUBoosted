import pandas as pd
from enum import Enum
import numpy as np
import time
import visualization as v

class Elo(Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    DIAMOND = 4

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

    elos = placements.iloc[:,0].apply(elo_to_enum)
    placements.iloc[:,0] = elos
    elos = placements.iloc[:,2].apply(elo_to_enum)
    placements.iloc[:,2] = elos


def rescale(data):
    data[:,:-1] -= np.mean(data[:,:-1], axis=0)
    data[:,:-1] /= np.std(data[:,:-1], axis=0)

    return data


def preprocess(my_df):
    df = my_df.copy()

    features = ['n_matches', 'kda', 'dmg', 'solo_q_tier','solo_q_division','flex_tier','flex_division']
    chosen_features = ['n_matches', 'kda', 'dmg', 'solo_q_tier']

    # Translate elos to numbers
    placements = df.loc[:, features[-4:]] # The last 4 features are tiers and divisions
    set_elos(placements)
    df.loc[:, features[-4:]] = placements

    data_set = df.loc[:, chosen_features].as_matrix()
    # data_set = rescale(data_set)

    return data_set


df = pd.read_csv('_dataset.txt', sep='\t')
data_set = preprocess(df)

# v.show_3d(data_set)
v.show_2d(data_set[:,1:])









