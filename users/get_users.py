"""
We're going to get a list of users by merging the list of users from
each contest. This doesn't get all Codeforces users, but it should hopefully
get the most active ones.
"""

import hashlib
import json
import re
import sys
import time
import urllib

from collections import defaultdict

WAIT_TIME = 0.6
CF_API_URL = "http://codeforces.com/api/{0}"

CF_API_KEY = "8e85b1647c2ef8492fa4596e2af86888f932d825"
CF_API_SECRET = "c33b1bf5ca60f4737759780c779c216991e63048"

OUT_FILE = 'tmp/out{0}.txt'
JOB_FILE = 'tmp/job{0}.txt'

user_handles = defaultdict(int)
failures = []

def rand_string(l=6):
    return "AAAAAA"

def repeat_try(f, cond, return_on_fail=None, mx_repeats=5):
    for _ in xrange(mx_repeats):
        out = f()
        if cond(out):
            return out
    print ("Failed to execute")
    return return_on_fail

def is_my_turn(job_no):
    MX_JOBS = 38
    unix_time = time.time()
    base = int(unix_time) - (int(unix_time) % (int(MX_JOBS * WAIT_TIME) + 1))
    # This guarantees everything is at least 0.3s apart
    if WAIT_TIME * job_no + .25 < unix_time - base < WAIT_TIME * (job_no + 1) - .25:
        return True
    return False

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
    out = []
    for match in re.finditer('\"handle\":\"(.*?)\"', standings):
        out.append(match.group(1))
    return out

def main(job_no):
    with open(JOB_FILE.format(job_no)) as f:
        for line in f:
            def users_in_contest():
                i = int(line)
                api_url = get_url('contest.standings', {
                        'contestId': str(i),
                        'showUnofficial': "true",
                        'apiKey': CF_API_KEY,
                        'time': str(int(time.time()))
                    })

                while not is_my_turn(job_no):
                    time.sleep(0.01)
                print (api_url)
                res = urllib.urlopen(api_url).read()
                users = get_users(res)
                return users

            def ok(users):
                return (len(users) > 0)

            users = repeat_try(users_in_contest, ok, [])

            ct = 0
            for user in users:
                ct += 1
                user_handles[user] += 1
            print ('Number of contestants:', ct)
            if ct == 0:
                print ('COULD NOT RETRIEVE RESULTS FOR CONTEST', line)
                failures.append(line)

    print ('FINISHED')
    print ('Failures:', failures)

    with open(OUT_FILE.format(job_no), 'w') as f:
        for user in user_handles:
            f.write(user + '\n')

if __name__ == '__main__':
    main(int(sys.argv[1]))