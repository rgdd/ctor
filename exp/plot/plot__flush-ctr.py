#!/usr/bin/python

import sys
import json
import logging
import plotter

log = logging.getLogger(__name__)

__in_path = "../flush/output.json"
__out_path = "flush-ctr.pdf"

def main():
    log.info("plotting based on: {}".format(__in_path))
    plotter.plot(
        parse(read(__in_path)),
        __out_path,
        "memory (MiB)",
        "number of queries (k)",
        "Probability that a flush succeeds",
    )
    log.info("results stored: {}".format(__out_path))

def read(path):
    with open(path, "r") as f:
        return json.load(f)

def parse(data):
    to_plot = []
    for pr, mem in data.items():
        parsed = { int(m)/(1024**2): mem[m] for m in mem }
        memory = sorted(parsed.keys())
        queries = [ parsed[mem]/1000 for mem in memory ]
        to_plot += [ (memory, queries, pr) ]
    return to_plot

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
