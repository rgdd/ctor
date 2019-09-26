#!/usr/bin/python3

#
# sim.py
# Simulate the number of SFO submissions needed to flush a single CTR with a
# given probability and available SFO memory.
#

import sys
import math
import json
import logging

log = logging.getLogger(__name__)

# Different probabilities to succeed with flushing
__PR = [ .9, .99, .999 ]
# Assumed memory available to store SFOs: 128MiB,256MiB,...,1024MiB
__SFO_MEM = [ i * 1024**2 for i in range(128, 1025, 128) ]
# Assumed SFO-size based on probing Alexa top-10k
__SFO_SIZE = 5323 + 3*128
__PATH = "output.json"

def main():
    log.info("generating flush data")
    err = write(sim(__PR, __SFO_MEM, __SFO_SIZE), __PATH)
    if err is not None:
        log.error(err)
        return 1
    log.info("results stored: {}".format(__PATH))

def sim(pr_list, mem_list, sfo_size):
    results = {}
    for pr in pr_list:
        results[pr] = {}
        for sfo_mem in mem_list:
            num_entries = sfo_mem / sfo_size
            results[pr][sfo_mem] = required_submissions(pr, num_entries)
    return results

def required_submissions(pr_to_success, num_entries):
    return math.log(1 - pr_to_success) / math.log(1 - (1/num_entries))

def write(data, path):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return None
    except Exception as e:
        return "failed writing to {} => {}".format(path, e)

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
