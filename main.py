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


sf = stf.StatisticsFetcher(verbose=True)
# Build cache starting from args
# sf.cache_all_summoners(sys.argv[2])

# Build cache starting from index
# sf.cache_all_summoners(10618)

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

# df = pd.read_csv('dataset2.txt', sep='\t')
# features = list(df)
# chosen = np.array(['n_matches', 'kda', 'win_rate', 'dmg', 'solo_q_tier'])
# visualize(df, chosen)
#
# data_set, df = pp.preprocess(df, 4, features, chosen)
# benchmark(data_set)
#

# sf.cache_all_matches(start=12)

# sf.cache_all_matches(int(sys.argv[2]), int(sys.argv[3]))
# sf.cache_all_matches(6000, 6999)

list = [1000194555,1000201688,1000218464,1000258408,1000267063,1000267579,1000273278,1000329489,1000389775,1000427366,1000427897,1000439297,1000516207,1000528396,1000698946,1000736261,1000741010,1000749614,1000754478,1000757710,1000784025,1000786660,1000787402,1000806271,1000851333,1000907186,1000928367,1000968686,1000975545,1000992087,1001032665,1001033304,1001044450,1001080919,1001097297,1001286571,1001458224,1001462299,1001467790,1001573340,1001581239,1001629592,1001703366,1001794898,1001951137,1001957989,1001961402,1001975244,1002025648,1002030663,1002087707,1002136668,1002138581,1002158124,1002202939,1002276701,1002278441,1002487952,1002512373,1002536980,1002560098,1002602776,1002627052,1002727486,1002731359,1002742494,1002871609,1002878288,1002937303,1003050886,1003070805,1003074154,1003132735,1003137127,1003178901,1003190347,1003227373,1003230298,1003324514,1003353448,1003395449,1003416493,1003591251,1003596826,1003661184,1003671251,1003681682,1003720958,1003731723,1003833855,1003844251,1003894016,1003901681,1003945069,1003986034,1004030976,1004038994,1004086979,1004090747,1004260563,1004264220,1004303733,1004334485,1004354220,1004354856,1004359215,1004394382,1004398457,1004440131,1004448734,1004479980,1004496507,1004499155,1004500775,1004569230,1004578623,1004688004,1004797002,1004935933,1004940835,1004962366,1005001170,1005188550,1005195277,1005223860,1005229869,1005396193,1005469138,1005491727,1005514239,1005528900]
sf.cache_matches(list)

