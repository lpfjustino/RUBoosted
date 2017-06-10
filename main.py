import urllib3
import requests
import pandas as pd
import player_base as pb
import numpy as np
import matplotlib.pyplot as plt

import summoner as s
import stats_fetcher as sf
import ds_builder as dsb
import sys
import time
import preprocessor as pp
import visualization as v
from sklearn.neural_network import MLPClassifier

# Build cache starting from args
#sf.cache_all_summoners(sys.argv[2])

# Build cache starting from index
#sf.cache_all_summoners(10618)

# Build dataset from cache starting from index
# dsb.dataset_v1(0)

df = pd.read_csv('dataset2.txt', sep='\t')
features = list(df)
chosen = np.array(['n_matches','kda', 'win_rate', 'dmg', 'solo_q_tier'])

data_set, df = pp.preprocess(df, 4, features, chosen)

v.show_2d(df, chosen[[1,2,4]])
# v.show_2d(df, chosen[[2,3,4]])
# v.show_3d(data_set[:,:])


X = data_set[:,:-1]
y = data_set[:,-1]

mlp = MLPClassifier(hidden_layer_sizes=(3,), max_iter=10, alpha=1e-4,
                    solver='sgd', verbose=10, tol=1e-4, random_state=1,
                    learning_rate_init=.1)
# mlp.fit(X,y)
# print("Training set score: %f" % mlp.score(X, y))
# print("Test set score: %f" % mlp.score(X_test, y_test))


def classify():
    pass