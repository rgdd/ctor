#!/usr/bin/python3

#
# Usage: ./sim.py --pr .5 > data/ram/0.50
# Usage: ./sim.py --pr .5 --disk > data/disk/0.50
#

from __future__ import division
from math import log

import sys
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="Flushing statistics")
    parser.add_argument("--pr",
        type=float, default=.5, action="store",
        help="Probability to succeed with flush")
    parser.add_argument("--entry-size",
        type=int, default=5323+3*128, action="store",
        help="Assumed size of certificate chain and SCTs")
    parser.add_argument("--disk",
        default=False, action="store_true",
        help="Simulate a RAM memory, otherwise a disk memory")

    args = parser.parse_args()
    if not 0 < args.pr < 1:
        logging.critical("invalid probability")
        return 1

    if args.disk:
        write(sim(args.pr, args.entry_size, 1, 32, 1, 1024**3))
    else:
        write(sim(args.pr, args.entry_size, 128, 1024, 128, 1024**2))
    
    return 0

def write(sim_results):
    for entry in sim_results:
        print(entry[0], entry[1])

def sim(pr, entry_size, start, end, interval, factor):
    ret = []
    for i in range(start, end, interval):
        cache_size = i * factor
        entries = cache_size / entry_size
        ret.append((cache_size, required_queries(pr, entries)))
    return ret

def required_queries(pr_to_success, num_entries):
    '''
    Pr["Not select target entry"] = q
    Pr["Not select target entry k times"] = q^k
    Pr["Success flush with k queries"] = 1 - q^k
    1 - Pr["Success flush with k queries"] = q^k
    k = log(1 - Pr["Success flush with k queries"]) / log(q)
    '''
    q = 1 - (1/num_entries)
    k = log(1 - pr_to_success) / log(q)
    return k

if __name__ == "__main__":
    sys.exit(main())
