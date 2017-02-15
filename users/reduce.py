import random

OUT_FILE = 'all_users.txt'

NUM_JOBS = 35

IN_PATH = 'tmp/out{0}.txt'

all_users = {}

for i in range(NUM_JOBS):
    with open(IN_PATH.format(i)) as f:
        for line in f:
            all_users[line.strip()] = True

user_list = list(all_users.iterkeys())
random.shuffle(user_list)

with open(OUT_FILE, 'w') as f:
    for user in user_list:
        f.write(user + '\n')