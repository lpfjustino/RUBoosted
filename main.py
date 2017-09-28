import numpy as np
import pandas as pd
from scipy.sparse.linalg.eigen.arpack._arpack import dsaupd
from sklearn import svm
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from ml import preprocessor as pp
from tools import visualization as v
from ml import ds_builder as ds

data_set_file = 'ml/resources/datasets/working/pp_DS.tsv'
split_datasets_folder = 'ml/resources/datasets/all_champs/split/'
split_datasets_names = ds.combine_into_labels(ds.all_riot_roles, ['DS.tsv'])

def visualize(df, chosen):
    print(df[:,chosen[1,8]])
    v.show_2d(df, chosen[[1,7,19]])
    v.show_2d(df, chosen[[2,3,4]])
    # v.show_3d(data_set[:,:])

def benchmark(data_set):
    X = data_set[:, :-1]
    y = data_set[:, -1]

    mlp = MLPClassifier(hidden_layer_sizes=(300,10), max_iter=1000, alpha=1e-4,
                        solver='sgd', verbose=0, tol=1e-5, random_state=1,
                        learning_rate_init=.2)
    mlp.fit(X, y)
    scores = cross_val_score(mlp, X, y, cv=10)

    clf = svm.SVC(kernel='linear', C=1)
    clf.fit(X, y)
    scores2 = cross_val_score(clf, X, y, cv=5)

    knn = KNeighborsClassifier(n_neighbors=3, weights='distance')
    knn.fit(X, y)
    scores3 = cross_val_score(knn, X, y, cv=5)

    print('MLP:', scores)
    print('SVM: ', scores2)
    print('KNN: ', scores3)

def benchmark_best_SVM(data_set, mode='ovo'):
    X = data_set[:, :-1]
    y = np.array(data_set[:, -1], dtype=int)

    clf = svm.SVC(kernel='rbf', C=30, gamma=0.001, tol=1e-3, probability=False, decision_function_shape=mode)
    print('Classifying')
    scores = cross_val_score(clf, X, y, cv=10)
    print(scores)
    print(max(scores), np.average(scores))

def tune_SVM(data_set):
    X = data_set[:, :-1]
    y = np.array(data_set[:, -1], dtype=int)

    # Cs = [0.001, 0.01, 0.1, 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 100, 1000]
    # gammas = [0.0001, 0.0025, 0.005, 0.0075, 0.001, 0.025, 0.005, 0.075, 0.01, 0.1, 1]
    # shapes = ['ovo', 'ovr']
    Cs = [25, 27, 30, 33, 35]
    gammas = [0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.001]
    shapes = ['ovo']
    param_grid = {'C': Cs, 'gamma': gammas, 'decision_function_shape': shapes}
    grid_search = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=10, verbose=True)
    grid_search.fit(X, y)
    print(grid_search.best_params_)
    print(grid_search.best_score_)

for ds in split_datasets_names:
    data_set_file = split_datasets_folder + ds

    print(ds)
    df = pd.read_csv(data_set_file, sep='\t', index_col=False)
    features = list(df)

    # Ignoring nick, flex elo and divisions
    chosen = list(df.iloc[:,:-3].columns.values)

    data_set, df = pp.preprocess(df, 4, features, chosen)
    # visualize(df, chosen)

    benchmark_best_SVM(data_set)

# Initializing statistics fetcher
# sf = stf.StatisticsFetcher(verbose=True)

# Build cache with limits set by args
# sf.cache_all_matches(int(sys.argv[2]), int(sys.argv[3]))

# Build cache starting from args
# sf.cache_all_summoners(sys.argv[2])

# tune_SVM(data_set)
