JOB_PATH = 'tmp/job{0}.txt'
NUM_JOBS = 35
ct = 0
for j in range(NUM_JOBS):
    with open(JOB_PATH.format(j), 'w') as f:
        for i in range(20):
            ct += 1
            f.write(str(ct) + '\n')

