import os
import json
from collections import defaultdict
import sys

MX_JOB_NO = 200
MX_DIFF_SIZE = None

DATA_DIR = 'tmp'
LOG_FILE = 'log.json'

OUT_PATH_BUGGY = 'buggy.json'
OUT_PATH_REPAIRED = 'repaired.json'

join = os.path.join
isfile = os.path.isfile

def is_int_str(s):
    try:
        v = int(s)
        return True
    except:
        return False

def get_submissions(prob_path):
    for f in os.listdir(prob_dir):
        if not is_int_str(f.split('.')[0]):
            continue
        yield f

# Copied from https://rosettacode.org/wiki/Longest_common_subsequence#Python
def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the subsequence out from the matrix
    result = []
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result

def diff_size(f1, f2):
    with open(f1) as f:
        a1 = f1.readlines()

    with open(f2) as f:
        a2 = f2.readlines()

    return max(len(a1), len(a2)) - lcs_len(a1, a2)

def parse(log_path):
    # Returns a dict which takes [handle][probid] -> [API objs]
    out = defaultdict(list)
    with open(log_path) as f:
        for line in f:
            obj = json.loads(line)
            con_id = obj['contestId']
            prob_id = obj['problem']['index']
            handle = obj['author']['members'][0]['handle']
            prob = str(con_id) + str(prob_id)
            out[(handle, prob)].append(line)
    return out

def main():
    out_f_buggy = open(OUT_PATH_BUGGY, 'w')
    out_f_repaired = open(OUT_PATH_REPAIRED, 'w')

    for i in range(MX_JOB_NO):
        job_dir = join(DATA_DIR, str(i))
        if not os.path.exists(job_dir):
            continue
        print (i)
        subs_by_handle_problem = parse(join(job_dir, LOG_FILE))
        for (handle, problem) in subs_by_handle_problem:
            corr = []
            incorr = []
            print (handle, problem)
            for sub_desc in subs_by_handle_problem[(handle, problem)]:
                sub_info = json.loads(sub_desc.strip())
                if sub_info['verdict'] == 'OK':
                    corr.append(sub_info)
                else:
                    incorr.append(sub_info)
            if len(corr) > 1:
                # Don't bother for now
                continue
            for sub_info in incorr:
                if diff_size(corr[0]['src_path'], sub_info['src_path']) < MX_DIFF_SIZE:
                    out_f_buggy.write(json.dumps(desc) + '\n')
                    out_f_repaired.write(json.dumps(corr[0]) + '\n')

    out_f_buggy.close()
    out_f_repaired.close()


if __name__ == '__main__':
    MX_DIFF_SIZE = sys.argv[1]
    main()