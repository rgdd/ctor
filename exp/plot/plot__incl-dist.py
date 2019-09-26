#!/usr/bin/python3

import os
import sys
import json
import logging

import plotter

log = logging.getLogger(__name__)

__in_dirs = [
    ("../incl-dist/data__single-hop", "Successful single-hop queries"),
    ("../incl-dist/data__full-circuit", "Successful full-circuit queries"),
]
__url2op = {
    "https://ct2.digicert-ct.com/log/": "Digicert",
    "https://sabre.ct.comodo.com/": "Sectigo",
    "https://ct.cloudflare.com/logs/nimbus2019/": "Cloudflare",
    "https://ct.googleapis.com/logs/argon2019/": "Google",
}
__out_dir = "img"

def main():
    for (in_dir, title) in __in_dirs:
        timing, sr = parse(read(in_dir))
        plotter.cdf(timing,
            "{}/incl-dist__{}.pdf".format(__out_dir, title.split()[1]),
            "time (s)",
            title,
        )

        print("")
        print("Success rate and total queries ({})".format(title.split()[1]))
        for (rate,queries,op) in sr:
            print("{:12} {:.3} {:2}k".format(op, rate, queries/1000))
        print("")

def parse(data):
    log2timing = {}
    log2sr = {}
    for exit_fpr, exit_msms in data.items():
        for exit_msm in exit_msms:
            for log_url,results in exit_msm.items():
                log2timing.setdefault(log_url, [])
                log2sr.setdefault(log_url, {"success":0, "fail":0})
                for result in results:
                    if result > 0:
                        log2timing[log_url] += [ result ]
                        log2sr[log_url]["success"] += 1
                    else:
                        log2sr[log_url]["fail"] += 1
    timing = []
    for log_url in log2timing:
        timing += [ (log2timing[log_url], __url2op[log_url]) ]

    sr = []
    for log_url in log2sr:
        success, failure = log2sr[log_url]["success"], log2sr[log_url]["fail"]
        total = success + failure
        sr += [ (success/(total), total, __url2op[log_url]) ]

    return timing, sr

def read(path):
    data = {}
    for msm_dir in os.listdir(path):
        for exit_fpr in os.listdir("/".join((path, msm_dir))):
            json_path = "/".join((path, msm_dir, exit_fpr))
            with open(json_path, "r") as f:
                msm_data = json.load(f)
            data.setdefault(exit_fpr, [])
            data[exit_fpr] += [ msm_data ]
    return data

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
