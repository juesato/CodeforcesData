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
OUT_PATH_FIXES = 'fixes.json'

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
            result.append(a[x-1])
            x -= 1
            y -= 1
    return list(reversed(result))

def get_diff(a, b, cs):
    out = []
    i = 0
    ia = 0
    ib = 0
    while i < len(cs):
        cur_a, cur_b = [], []
        while cs[i] != a[ia]:
            cur_a.append(a[ia])
            ia += 1
        while cs[i] != b[ib]:
            cur_b.append(b[ib])
            ib += 1
        if len(cur_a) or len(cur_b):
            out.append((cur_a, cur_b))
        i += 1
        ia += 1
        ib += 1
    return out

def diff(f1, f2):
    with open(f1) as f:
        a1 = f.readlines()

    with open(f2) as f:
        a2 = f.readlines()

    diff_size = max(len(a1), len(a2)) - len(lcs(a1, a2))

    diff_out = None
    if diff_size <= MX_DIFF_SIZE:
        diff_out = get_diff(a1, a2, lcs(a1, a2))

    return diff_size, diff_out

def parse(log_path):
    # Returns a dict which takes [handle][probid] -> [API objs]
    out = defaultdict(list)
    with open(log_path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except:
                print "failed to parse line " + line
                continue
            con_id = obj['contestId']
            prob_id = obj['problem']['index']
            handle = obj['author']['members'][0]['handle']
            prob = str(con_id) + str(prob_id)
            out[(handle, prob)].append(line)
    return out

def main():
    out_f_buggy = open(OUT_PATH_BUGGY, 'w')
    out_f_repaired = open(OUT_PATH_REPAIRED, 'w')
    out_f_fixes = open(OUT_PATH_FIXES, 'w')

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
            if len(corr) != 1:
                continue
            for sub_info in incorr:
                diff_size, maybe_diff = diff(corr[0]['src_path'], sub_info['src_path'])
		if diff_size <= MX_DIFF_SIZE:
                    out_f_buggy.write(json.dumps(sub_info) + '\n')
                    out_f_repaired.write(json.dumps(corr[0]) + '\n')
                    out_f_fixes.write(json.dumps(maybe_diff) + '\n')
        exit(0)
    out_f_buggy.close()
    out_f_repaired.close()
    out_f_fixes.close()

if __name__ == '__main__':
    MX_DIFF_SIZE = int(sys.argv[1])
    main()
