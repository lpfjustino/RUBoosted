import urllib3
import requests

import player_base as pb
import numpy as np
import matplotlib.pyplot as plt

import summoner as s
import stats_fetcher as sf

sf.cache_all_summoners(1317)

# print('begun')
# a = s.get_cached_summoners_instances()
# print('read')
# n_matches = []
# print('iterating')
# for pl in a:
#     s8 = sf.filter_s8_matches(pl)
#     n_matches.append(len(s8))
#
# print(len(a), ' analyzed')
# print(n_matches)
