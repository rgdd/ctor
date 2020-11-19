#!/usr/bin/python3

import os
import sys
import json
import logging

import numpy as np

log = logging.getLogger(__name__)

def main():
    data = read("parsed")
    sfo_per_website_visit = extract_sfo_dist(data)
    sfo_summary = extract_sfo_summary(data)
    chain_bytes = [s["chain_bytes"] for s in sfo_summary]
    num_scts = [s["num_sct"] for s in sfo_summary]

    log.info("avg num of sfos per website: {:.1f}".format(
        np.mean(sfo_per_website_visit),
    ))
    log.info("Avg chain len: {:.1f} bytes".format(np.mean(chain_bytes)))
    log.info("Max chain len: {:.1f} bytes".format(np.max(chain_bytes)))
    log.info("Avg num of SCTs per chain: {:.1f}".format(np.mean(num_scts)))

def read(dir_path):
    data = []
    for filename in os.listdir(dir_path):
        with open("/".join((dir_path, filename))) as f:
            data.append(json.load(f))
    return data

def extract_sfo_dist(data):
    sfo_per_website_visit = []
    for sfo_list in data:
        sfo_per_website_visit.append(len(sfo_list))
    return sfo_per_website_visit

def extract_sfo_summary(data):
    processed_serial_numbers, sfo_summary = {}, []
    for measurement in data:
        for sfo_info in measurement:
            chain_len, chain_bytes, num_sct, serial_number, cn = sfo_info
            if serial_number in processed_serial_numbers:
                log.debug("duplicate: {} ({})".format(serial_number, cn))
                continue

            processed_serial_numbers[serial_number] = True
            sfo_summary.append({
                "chain_len": chain_len,
                "chain_bytes": chain_bytes,
                "num_sct": num_sct,
            })

            if num_sct == 0 or num_sct > 5:
                log.debug("{} => {} ({})".format(num_sct, serial_number, cn))
    return sfo_summary

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
