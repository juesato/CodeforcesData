import os

USERNAME_PATH = os.path.join(
    os.path.dirname(os.getcwd()), 'users/all_users.txt')
JOB_PATH = 'tmp/job{0}.txt'

# Each job should be ~1000 users
# I believe this will make each job take ~8 hours
USERS_PER_JOB = 1000

jobs_file = None

with open(USERNAME_PATH) as f:
    for i, line in enumerate(f):
        if i % USERS_PER_JOB == 0:
            if jobs_file:
                jobs_file.close()
            jobs_file_no = int(i / USERS_PER_JOB) + 1 # 0 is my debug job
            jobs_file = open(JOB_PATH.format(jobs_file_no), 'w')
        jobs_file.write(line)

if jobs_file:
    jobs_file.close()