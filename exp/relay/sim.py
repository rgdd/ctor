#!/usr/bin/env python3

import sys
import json
import logging
import argparse

log = logging.getLogger(__name__)

from relay import Relay

def main():
    seconds = 3600*24*1
    #data = sim([1/4096], [0.01, 0.02, 0.04, 0.08], seconds)
    data = sim([1/4096], [0.01, 0.05, 0.10, 0.15, 0.20], seconds)
    with open("pr.json", "w") as f:
        json.dump(data, f, indent=2)

    #data = sim([1/1024, 1/2048, 1/4096, 1/8192], [0.01], seconds)
    #with open("fraction.json", "w") as f:
    #    json.dump(data, f, indent=2)

def sim(fractions, tb_prs, seconds):
    data = {}
    for fraction in fractions:
        log.info("processing fraction: {}".format(fraction))
        data.setdefault(fraction, {})
        for tb_pr in tb_prs:
            log.info("processing tb_pr: {}".format(tb_pr))
            data[fraction][tb_pr] = []
            r = Relay(fraction, tb_pr, 0)
            for time in range(seconds):
                if time%60 == 0:
                    status = r.status()
                    data[fraction][tb_pr] += [{
                        "time": status[0],
                        "circuit_count": status[1],
                        "submitted_sfo_count": status[2],
                        "processed_sfo_count": status[3],
                        "cache_hit_count": status[4],
                        "pending_hit_count": status[5],
                        "auditor_submission_count": status[6],
                        "pending_sfo_entries": status[7],
                        "cache_entries": status[8],
                    }]
                r.tick()
    return data

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
