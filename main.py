import urllib3
import requests

import player_base as pb
import numpy as np

from summoner import Summoner

# s = Summoner("Luispfj")
# s.serialize_summoner()
#
# is_s8_match = lambda match: match['season'] == 8
# season8 = [is_s8_match(match) for match in s.matches]
# matches = np.array(s.matches)
# s8matches = matches[season8]

with open('base.txt', encoding="utf8") as f:
    content = f.readlines()[0]
    summoners = str.split(content,',')

for summoner in summoners:
    print(summoner)
    s = Summoner(summoner)
    s.serialize_summoner()

    is_s8_match = lambda match: match['season'] == 8
    season8 = [is_s8_match(match) for match in s.matches]
    matches = np.array(s.matches)
    print(len(matches))
    s8matches = matches[season8]

    print(len(s8matches))

