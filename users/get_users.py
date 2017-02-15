"""
We're going to get a list of users by merging the list of users from
each contest. This doesn't get all Codeforces users, but it should hopefully
get the most active ones.
"""

import json
import time
import hashlib
import urllib
import re
from collections import defaultdict

MAX_CF_CONTEST_ID = 700

CF_API_URL = "http://codeforces.com/api/{0}"

CF_API_KEY = "8e85b1647c2ef8492fa4596e2af86888f932d825"
CF_API_SECRET = "c33b1bf5ca60f4737759780c779c216991e63048"

OUT_FILE = 'user_handles.txt'

user_handles = defaultdict(int)

def rand_string(l=6):
    return "AAAAAA"

def get_url(method_name, arg_dict):
    sorted_args = sorted(arg_dict.iterkeys(), key=lambda k: (k, arg_dict[k]))
    params = '?'
    for arg in sorted_args:
        params += arg + '=' + arg_dict[arg] + '&'
    params = params.strip('&')

    rand = rand_string()
    apiSig = rand + '/' + method_name + params + '#' + CF_API_SECRET
    sha = hashlib.sha512()
    sha.update(apiSig)
    apiSigHash = sha.hexdigest()

    url = CF_API_URL.format(method_name) + params + \
        '&apiSig=' + rand + apiSigHash
    return url

def get_users(standings):
    # I'm using the raw string because I think loading it as a JSON
    # object was taking too long
    for match in re.finditer('\"handle\":\"(.*?)\"', standings):
        yield match.group(1)

for i in range(MAX_CF_CONTEST_ID):
    time.sleep(0.2) # for the CF API
    api_url = get_url('contest.standings', {
            'contestId': str(i),
            'showUnofficial': "true",
            'apiKey': CF_API_KEY,
            'time': str(int(time.time()))
        })

    print (api_url)
    res = urllib.urlopen(api_url).read()
    users = get_users(res)
    ct = 0
    for user in users:
        ct += 1
        user_handles[user] += 1
    print ('Number of contestants:', ct)

with open(OUT_FILE, 'w') as f:
    for user in users:
        f.write(user + '\n')
