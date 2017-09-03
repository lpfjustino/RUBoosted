import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from ml import preprocessor as pp
from tools import visualization as v
from ml.ds_builder import combine_into_labels, all_roles


def get_short_chosen():
    # roles = json.loads(open('ml/roles.txt', 'r').read())
    # all_roles = np.unique([role['role'] for role in roles])
    # stats_names = ['weights', 'avg_kda', 'avg_dmg', 'avg_wr']
    stats_names = ['weights', 'avg_kda', 'avg_dmg', 'avg_wr', 'var_kda', 'var_dmg']

    return combine_into_labels(all_roles, stats_names)

def visualize(df, chosen):
    print(df[:,chosen[1,8]])
    v.show_2d(df, chosen[[1,7,19]])
    v.show_2d(df, chosen[[2,3,4]])
    dsa
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

def benchmark_SVM(data_set, mode='ovo'):
    X = data_set[:, :-1]
    y = data_set[:, -1]

    for i in range(5):
        clf = svm.SVC(kernel='linear', C=1, degree=i, tol=1e-3, verbose=False, decision_function_shape=mode)
        clf.fit(X, y)
        scores = cross_val_score(clf, X, y, cv=10)

        print('Degree:',i, max(scores), scores)

    clf = svm.SVC(kernel='poly', C=1, tol=1e-3, probability=True, decision_function_shape=mode)
    clf.fit(X, y)
    scores = cross_val_score(clf, X, y, cv=10)

    print("Poly:", max(scores), scores)

    clf = svm.SVC(kernel='sigmoid', C=1, tol=1e-3, probability=True, decision_function_shape=mode)
    clf.fit(X, y)
    scores = cross_val_score(clf, X, y, cv=10)

    print("Sigmoid:", max(scores), scores)

    # Cs = np.linspace(1e-2, 1, num=20)
    # for c in Cs:
    #     clf = svm.SVC(kernel='rbf', C=c, tol=1e-3, probability=True, decision_function_shape='ovr')
    #     clf.fit(X, y)
    #     scores = cross_val_score(clf, X, y, cv=10)
    #     print('Radial', c, max(scores))

def benchmark_best_SVM(data_set, mode='ovr'):
    X = data_set[:, :-1]
    y = np.array(data_set[:, -1], dtype=int)

    clf = svm.SVC(kernel='rbf', C=1, tol=1e-3, probability=False, decision_function_shape=mode)
    # clf.fit(X, y)
    # print('Model trained')
    print('Classifying')
    scores = cross_val_score(clf, X, y, cv=10)
    print(max(scores), scores)

print('Reading file')
df = pd.read_csv('ml/resources/DS.tsv', sep='\t', index_col=False)
print('File read')
features = list(df)

# Ignoring nick, flex elo and divisions
chosen = df.iloc[:,1:-3].columns.values

print('Preprocessing')
data_set, df = pp.preprocess(df, 4, features, chosen)
print('Preprocessed')
# visualize(df, chosen)

# chosen = np.array(['n_matches', 'kda', 'dmg', 'win_rate', 'var_kda', 'var_dmg', 'var_wr', 'kurt_kda', 'kurt_dmg', 'kurt_wr',
#                    'skew_kda', 'skew_dmg', 'skew_wr', 'solo_q_tier'])
# data_set, df = pp.preprocess(df, 4, features, chosen)
# print('\tOVR:')
# benchmark_SVM(data_set, 'ovr')
# print('\tOVO:')
# benchmark_SVM(data_set, 'ovo')
# print('\tBest SVM')
print('Training model')
benchmark_best_SVM(data_set)

# Initializing statistics fetcher
# sf = stf.StatisticsFetcher(verbose=True)

# Build cache with limits set by args
# sf.cache_all_matches(int(sys.argv[2]), int(sys.argv[3]))

# Build cache starting from args
# sf.cache_all_summoners(sys.argv[2])
