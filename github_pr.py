#!/usr/bin/python
import concurrent.futures
import json
import re
from operator import itemgetter
from pprint import pprint

import utils
from tqdm import tqdm


def checkstatus(repo_url, pr_ref):
    sc_url = repo_url + "/commits/" + pr_ref + "/statuses"
    utils.c_print(sc_url)
    sc_resp = utils.httpget(sc_url, headers=headers)
    if sc_resp.status_code == 200:
        sc = json.loads(sc_resp.content.decode('utf-8', 'ignore'))
        status_check = False
        # c_print(sc)
        if len(sc) > 0:
            utils.c_print(
                "Status Check for " + pr_ref + " updated at : " + sc[0]['updated_at'] + " " + sc[0]['state'] + "")
            return sc[0]['state']
        return None
    else:
        utils.c_print(
            "Error with response, status Code:" + sc_resp.status_code + ", Body" + sc_resp.content.decode('utf-8',
                                                                                                          'ignore'))
        return None


def checkreviews(repo_url, pull_number, pr_ref):
    rv_url = repo_url + "/pulls/" + str(pull_number) + '/reviews'
    utils.c_print(rv_url)
    rv_resp = utils.httpget(rv_url, headers=headers)
    rv = json.loads(rv_resp.content.decode('utf-8', 'ignore'))
    rv_approved = False
    for r in rv:
        if r['commit_id'] == pr_ref and r['state'] == 'APPROVED':
            rv_approved = True
            utils.c_print(
                "Pull Request " + str(pull_number) + " Approved by " + r['user']['login'] + " on " + r['submitted_at'])

    utils.c_print("Pull Request " + str(pull_number) + " Not Approved") if not rv_approved else None

    return len(rv), rv_approved


def pullstatus(p):
    pr_number = p['number']
    pr_ref = p['head']['sha']
    pr_reviewers = p['requested_reviewers']
    reviewer = []

    [reviewer.append(pr_reviewer['login']) for pr_reviewer in pr_reviewers if len(pr_reviewers) > 0]

    reviewers = True if len(reviewer) > 0 else False

    pr_status = checkstatus(repo_url, pr_ref)
    rv_count, pr_review = checkreviews(repo_url, pr_number, pr_ref)

    if pr_status == 'failure' or pr_status == 'error':
        pr_state = 'FAILING'
    elif not reviewers and rv_count == 0:
        pr_state = 'REVIEWER_PENDING'
    elif (not reviewers and rv_count > 0 and not pr_review) or (reviewers and not pr_review):
        pr_state = 'REVIEW_IN_PROGRESS'
    elif pr_review and (pr_status == 'pending' or pr_status is None):
        pr_state = 'STATUS_CHECK_PENDING'
    elif pr_review and pr_status == 'success':
        pr_state = 'MERGE_PENDING'
    else:
        pr_state = 'UNKNOWN_STATE'

    data = {'id': pr_number, 'state': pr_state}

    # print(reviewers, rv_count, pr_review, pr_status)
    # print(data)
    return data


def pullrequest(url):
    global next_page, headers, pr_url, repo_url, pr_result, thread_workers

    utils.c_print(url);
    pr_resp = utils.httpget(url, headers=headers)
    next_pr_url = [re.search('\<(.*?)\>', link).group(1) for link in pr_resp.headers.get('Link', '').split(',') if
                   '; rel="next"' in link]
    next_pr_url.sort()
    next_page = False if len(next_pr_url) == 0 else True
    pr_url = None if len(next_pr_url) == 0 else next_pr_url[0]

    if pr_resp.status_code == 200:
        pr = json.loads(pr_resp.content.decode('utf-8', 'ignore'))

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_workers) as executor:
            child_thread = {executor.submit(pullstatus, p): p for p in pr}
            for future in tqdm(concurrent.futures.as_completed(child_thread)):
                p = child_thread[future]
                try:
                    data = future.result()
                except Exception as exc:
                    utils.c_print("Thread Exception for Pull Request : " + p['number'] + " Error :" + format(exc))
                    data = {'id': p['number'], 'state': 'REQUEST_EXCEPTION'}
                finally:
                    if len(data) > 0:
                        pr_result.append(data)
    else:
        utils.c_print(
            "Error with response, URL: " + pr_resp.url + " status Code:" + pr_resp.status_code + ", Body" + pr_resp.content.decode(
                'utf-8', 'ignore'))


def fetchprstatus(owner, repo, token):
    global next_page, headers, pr_url, repo_url, pr_result, thread_workers
    pr_result = []
    thread_workers = 50
    utils.debug = False
    next_page = True
    headers = {'Authorization': 'token  ' + token}
    repo_url = "https://api.github.com/repos/" + owner + "/" + repo
    pr_url = repo_url + "/pulls"
    while next_page:
        if pr_url is not None:
            pullrequest(pr_url)

    return json.dumps({'prs': sorted(pr_result, key=itemgetter('id'), reverse=True)})


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        owner = sys.argv[1]
        repo = sys.argv[2]
        token = sys.argv[3]
        pprint(fetchprstatus(owner, repo, token))
    else:
        print("This script will take exactly three(3) arguments")
        print("Invoke this script as ./GitHubPR.py owner repo token")
