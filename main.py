import urllib3
import requests

import player_base as pb
import numpy as np

from summoner import Summoner

s = Summoner("Luispfj")
s.serialize_summoner()

is_s8_match = lambda match: match['season'] == 8
season8 = [is_s8_match(match) for match in s.matches]
a = np.array(s.matches)
test = a[season8]
print(len(test))