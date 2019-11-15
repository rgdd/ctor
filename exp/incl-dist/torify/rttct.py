#!/usr/bin/env python3

import os
import sys
import json
import logging
import requests
import argparse

log = logging.getLogger(__name__)

def main(args):
    log2sct, err = sct_populate(args.input)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("using SCTs from {} logs".format(len(log2sct.keys())))

    log2sth, err = sth_populate(log2sct.keys(), args.timeout)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("downloaded one STH per log")

    err = write(job(log2sct, log2sth, args.timeout), args.output)
    if err is not None:
        log.error(err)
        sys.exit(1)
    log.info("stored results: {}".format(args.output))

def job(log2sct, log2sth, timeout):
    '''
    Measure how long it takes to query different CT logs for inclusion proofs.
    '''
    dist = {}
    for log_url, tree_size in log2sth.items():
        sth_url = "".join((log_url, "ct/v1/get-sth"))
        incl_url = "".join((log_url, "ct/v1/get-proof-by-hash"))
        dist[log_url] = []

        # Warmup query that leaves established connection open
        s = requests.Session()
        get_sth_size(s, sth_url, timeout)

        # Timed inclusion queries
        for sct_hash in log2sct[log_url]:
            params = {
                "hash": sct_hash,
                "tree_size": tree_size,
            }
            dist[log_url] += [ timed_query(s, incl_url, params, timeout) ]
    return dist

def timed_query(session, incl_url, params, timeout):
    try:
        r = session.get(incl_url, params=params, timeout=timeout)
        return -1 if r.status_code != 200 else r.elapsed.total_seconds()
    except:
        return -2

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
        return None, "failed fetching {} => {}".format(url, e)

def write(data, path):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return None
    except Exception as e:
        return "failed writing to: {} => {}".format(path, e)

def get_args():
    parser = argparse.ArgumentParser(description="Timed inclusion queries")
    parser.add_argument("-i", "--input",
        type=str, action="store", default="../tor/scthash.json",
        help="Path to the SCT data set collected by <add link>",
    )
    parser.add_argument("-o", "--output",
        type=str, action="store", default="output.json",
        help="Path where json-encoded output should be stored",
    )
    parser.add_argument("-t", "--timeout",
        type=int, action="store", default=10,
        help="Seconds to wait while establishing connection and reading",
    )
    return parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main(get_args()))
