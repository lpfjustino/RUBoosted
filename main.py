import urllib3
import requests

import player_base as pb
import numpy as np
import matplotlib.pyplot as plt

import summoner as s
import stats_fetcher as sf
import ds_builder as dsb
import sys
import time

#sf.cache_all_summoners(sys.argv[2])
#sf.cache_all_summoners(10618)

dsb.dataset_v1()