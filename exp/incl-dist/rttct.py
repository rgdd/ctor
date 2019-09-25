#!/usr/bin/env python2

"""
Exitmap module that determines the distribution of CT logs' responsiveness
while querying for inclusion proofs.  Read more about exitmap modules here:

https://github.com/NullHypothesis/exitmap
"""

import os
import sys
import json
import logging
import requests

import torsocks
import util

log = logging.getLogger(__name__)

# A dictionary that maps a CT log URL to a list of base64-encoded SCT hashes.
# This is populated by setup() by reading a data set located at `PATH`.  For
# more info regarding the data set and how to obtain it, see
# <add link>
SCT, PATH = None, "/home/rasmdahl/ctor/scthash.json"

# A dictionary that maps a CT log URL to a valid STH size.  This is populated
# by setup() by querying the logs found in `SCT`.
STH = None

# Number of seconds to wait while establishing a connection and reading, see
# https://2.python-requests.org/en/master/user/advanced/
TIMEOUT = 10

def probe(exit_desc, run_python_over_tor, run_cmd_over_tor, **kwargs):
    run_python_over_tor(job, exit_desc.fingerprint, STH, SCT, TIMEOUT)

def job(exit_fpr, sth, sct, timeout):
    '''
    A job that measures how long it takes to query different CT logs for
    inclusion proofs through a given exit relay.
    '''
    dist = {}
    for log_url, tree_size in sth.items():
        sth_url = "".join((log_url, "ct/v1/get-sth"))
        incl_url = "".join((log_url, "ct/v1/get-proof-by-hash"))
        dist[log_url] = []

        # Warmup query that leaves established connection open
        s = requests.Session()
        get_sth_size(s, sth_url, timeout)

        # Timed inclusion queries
        for sct_hash in sct[log_url]:
            params = {
                "hash": sct_hash,
                "tree_size": tree_size,
            }
            dist[log_url] += [ timed_query(s, incl_url, params, timeout) ]

    err = write("/".join((util.analysis_dir, exit_fpr)), dist)
    if err is not None:
        logging.warning("failed writing for {} => ".format(exit_fpr, err))

def setup():
    '''
    Initializes all jobs with relevant logs, SCT hashes, STH sizes, and a
    data directory for storing per exit-relay json-encoded distribution results.
    '''
    global SCT
    global STH

    SCT, err = sct_populate(PATH)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("using SCTs from {} logs".format(len(SCT.keys())))

    STH, err = sth_populate(SCT.keys(), TIMEOUT)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("downloaded one STH per log")

    err = create_data_dir(util.analysis_dir)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("created data directory: {}".format(util.analysis_dir))

def create_data_dir(path):
    try:
        os.makedirs(path)
        return None
    except Exception as e:
        return "failed creating {} => {}".format(util.analysis_dir, e)

def sct_populate(path):
    try:
        with open(path, "r") as f:
            return json.load(f), None
    except Exception as e:
        return None, "fail reading: {}".format(e)

def sth_populate(log_urls, timeout):
    sth = {}
    for url_log in log_urls:
        url_sth = "".join(((url_log), "ct/v1/get-sth"))
        sth_size, err = get_sth_size(requests, url_sth, timeout)
        if err is not None:
            return None, err
        sth[url_log] = sth_size
    return sth, None

def get_sth_size(session, url, timeout):
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code != 200 or "tree_size" not in r.json():
            return None, "invalid response for {}".format(url_sth)
        return r.json()["tree_size"], None
    except Exception as e:
        return "failed fetching {} => {}".format(url, e)

def timed_query(session, incl_url, params, timeout):
    try:
        r = session.get(incl_url, params=params, timeout=timeout)
        return -1 if r.status_code != 200 else r.elapsed.total_seconds()
    except:
        return -2

def write(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return None
    except Exception as e:
        return e

if __name__ == "__main__":
    log.critical("Module can only be run over Tor, and not stand-alone.")
