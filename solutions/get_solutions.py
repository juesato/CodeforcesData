import copy
import json
import re
import time, os, sys
import urllib
import shutil

start_time = time.time()
TOT_JOBS = None
WAIT_TIME = 0.3 # Everyone has to wait 0.3s between requests
LONG_WAIT_TIME = 1.0

MAX_SUBS = 1000000
MAX_CF_CONTEST_ID = 700
MAGIC_START_POINT = 0

JOB_FILE_FMT = 'tmp/job{0}.txt'
LOG_FILE_FMT = 'tmp/{0}/log.json'

# These strings are all fairly suspect except
SOURCE_CODE_BEGIN = 'program-source" style="padding: 0.5em;">'
OUTPUT_REGEX = re.compile('<div class="name">Participant\'s output</div>\s+<div class="text"><pre>(.*?)</pre>', re.DOTALL)
CHECKER_BEGIN = '<div class="name">Checker comment</div>\s+<div class="text"><pre>(.*?)[\s<]'

# The URLs are fine
SUBMISSION_URL = 'http://codeforces.com/contest/{ContestId}/submission/{SubmissionId}'
USER_INFO_URL = 'http://codeforces.com/api/user.status?handle={handle}&from=1&count={count}'

EXT = {'C++': 'cpp', 'C': 'c', 'Java': 'java', 'Python': 'py', 'Delphi': 'dpr', 'FPC': 'pas', 'C#': 'cs'}
EXT_keys = EXT.keys()

replacer = {'&quot;': '\"', '&gt;': '>', '&lt;': '<', '&amp;': '&', "&apos;": "'"}
keys = replacer.keys()

def wait_until_my_turn(job_no, wait_time=WAIT_TIME):
    CYCLE_SECS = int(TOT_JOBS * wait_time) + 1
    while True:
        unix_time = time.time()
        unix_time_int = int(unix_time)
        base = unix_time_int / CYCLE_SECS * CYCLE_SECS

        # Everyone owns a 0.3s window, during which you have 0.1s to make your request
        my_begin = base + wait_time * (0.5 + job_no) - 0.05
        my_end = base + wait_time * (0.5 + job_no) + 0.05
        if my_begin < unix_time < my_end:
            return
        time.sleep(0.01)

def get_ext(comp_lang):
    if 'C++' in comp_lang:
        return 'cpp'
    for key in EXT_keys:
        if key in comp_lang:
            return EXT[key]
    return ""

def parse(source_code):
    for key in keys:
        source_code = source_code.replace(key, replacer[key])
    return source_code

def extract_outputs(s):
    out = []
    ms = OUTPUT_REGEX.finditer(s)
    for match in ms:
        output = parse(match.group(1))
        out.append(output)

    corr = []
    ms = re.finditer(CHECKER_BEGIN, s)
    for match in ms:
        verd = match.group(1)
        corr.append(verd == "ok")

    assert len(corr) == len(out)
    return zip(out, corr)

def get_directory_path(handle, job_no, prob_num, contest_num):
    prob_dir = str(contest_num) + str(prob_num)
    return 'tmp/' + str(job_no) + '/' + handle + '/' + prob_dir

def get_submissions(handle, job_no):
    wait_until_my_turn(job_no, LONG_WAIT_TIME)
    user_info = urllib.urlopen(USER_INFO_URL.format(handle=handle, count=MAX_SUBS)).read()
    try:
        dic = json.loads(user_info)
    except ValueError as e:
        print e
        print (user_info)
    out = []
    if dic['status'] != u'OK':
        print 'Oops.. Something went wrong...'
        exit(0)

    submissions = dic['result']

    print ('Number of submissions', len(submissions))

    # print ('Getting submissions', time.time() - start_time)

    for submission in submissions:
        if submission['contestId'] >= MAX_CF_CONTEST_ID:
            continue

        # print (submission)
        verdict = submission['verdict']
        con_id, sub_id = submission['contestId'], submission['id'],
        prob_name, prob_id = submission['problem']['name'], submission['problem']['index']
        comp_lang = submission['programmingLanguage']

        wait_until_my_turn(job_no)
        submission_info = urllib.urlopen(SUBMISSION_URL.format(ContestId=con_id, SubmissionId=sub_id)).read()
        start_pos = submission_info.find(SOURCE_CODE_BEGIN, MAGIC_START_POINT)
        start_pos += len(SOURCE_CODE_BEGIN)
        end_pos = submission_info.find("</pre>", start_pos)
        src_code = parse(submission_info[start_pos:end_pos]).replace('\r', '')
        output_data = extract_outputs(submission_info)
        ext = get_ext(comp_lang)

        new_directory = get_directory_path(handle, job_no, prob_id, con_id)
        if not os.path.exists(new_directory):
            os.makedirs(new_directory)
        z = 1
        while os.path.exists(os.path.join(new_directory, '%s.json' % z)):
            z += 1

        src_path = os.path.join(new_directory, '%s.json' % z)
        src_file = open(src_path, 'w')
        src_file.write(src_code)
        src_file.close()

        out_dpath = os.path.join(new_directory, '%s_out.json' % z)
        out_dfile = open(out_dpath, 'w')
        out_dfile.write(json.dumps(output_data))
        out_dfile.close()

        out_info = copy.deepcopy(submission)
        out_info['src_path'] = src_path
        out_info['out_path'] = out_dpath
        out.append(out_info)

    end_time = time.time()
    print 'Execution time %d seconds' % int(end_time - start_time)
    return out


def main(job_no):
    log_file = open(LOG_FILE_FMT.format(job_no), 'w')
    with open(JOB_FILE_FMT.format(job_no)) as f:
        for line in f:
            try:
                handle = line.strip()
                results = get_submissions(handle, job_no)
                for result in results:
                    log_file.write(json.dumps(result) + '\n')

            except Exception as e:
                print ("Hm something went wrong", e)
                pass

    log_file.close()

if __name__ == '__main__':
    job_no = int(sys.argv[1])
    TOT_JOBS = int(sys.argv[2])
    # Since I just keep incrementing the file count, the only reasonable option is
    # every run should be fresh
    if os.path.exists('tmp/' + str(job_no)):
        shutil.rmtree('tmp/' + str(job_no))
    os.makedirs('tmp/' + str(job_no))
    main(job_no)
