import urllib3
import requests
import pandas as pd
import player_base as pb
import numpy as np
import matplotlib.pyplot as plt

import summoner as s
import stats_fetcher as stf
import ds_builder as dsb
import sys
import time
import preprocessor as pp
import visualization as v

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm

from sklearn.model_selection import cross_val_score


# Build dataset from cache starting from index
# dsb.dataset_v1(0)

def visualize(df, chosen):
    v.show_2d(df, chosen[[1,2,4]])
    v.show_2d(df, chosen[[2,3,4]])
    # v.show_3d(data_set[:,:])

def benchmark(data_set):
    X = data_set[:, :-1]
    y = data_set[:, -1]

    mlp = MLPClassifier(hidden_layer_sizes=(3,), max_iter=10, alpha=1e-4,
                        solver='sgd', verbose=0, tol=1e-4, random_state=1,
                        learning_rate_init=.1)
    mlp.fit(X, y)
    scores = cross_val_score(mlp, X, y, cv=5)

    clf = svm.SVC(kernel='linear', C=1)
    clf.fit(X, y)
    scores2 = cross_val_score(clf, X, y, cv=5)

    knn = KNeighborsClassifier(n_neighbors=3, weights='distance')
    knn.fit(X, y)
    scores3 = cross_val_score(knn, X, y, cv=5)

    print('MLP:', scores)
    print('SVM: ', scores2)
    print('KNN: ', scores3)

df = pd.read_csv('dataset2.txt', sep='\t')
features = list(df)
chosen = np.array(['n_matches', 'kda', 'win_rate', 'dmg', 'solo_q_tier'])

data_set, df = pp.preprocess(df, 4, features, chosen)
visualize(df, chosen)
benchmark(data_set)
#


# Initializing statistics fetcher
# sf = stf.StatisticsFetcher(verbose=True)

# Build cache with limits set by args
# sf.cache_all_matches(int(sys.argv[2]), int(sys.argv[3]))

# Build cache starting from args
# sf.cache_all_summoners(sys.argv[2])
