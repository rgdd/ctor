#!/usr/bin/python3

import os
import sys
import json
import logging

import plotter

log = logging.getLogger(__name__)

IN_DIRS = [
    ("../sfo-dist/parsed", "reddit"),
]
OUT_DIR = "img"

def main():
    for (in_dir, title) in IN_DIRS:
        data = read(in_dir)
        sfo_per_website_visit = extract_sfo_dist(data)
        plotter.cdf([
                (sfo_per_website_visit,title),
            ],
            "{}/sfo-dist.pdf".format(OUT_DIR),
            "number of SFOs per website",
        )

        sfo_summary = extract_sfo_summary(data)
        plotter.cdf([
                ([s["chain_len"] for s in sfo_summary], "reddit"),
            ],
            "{}/sfo-info__chain-len.pdf".format(OUT_DIR),
            "certificate chain size (number)",
        )
        plotter.cdf([
                ([s["chain_bytes"] for s in sfo_summary], "reddit"),
            ],
            "{}/sfo-info__chain-bytes.pdf".format(OUT_DIR),
            "certificate chain size (bytes)",
        )
        plotter.cdf([
                ([s["num_sfo"] for s in sfo_summary], "reddit"),
            ],
            "{}/sfo-info__sfo_num.pdf".format(OUT_DIR),
            "number of SCTs (end-entity certificates)",
        )

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
            chain_len, chain_bytes, num_sfo, serial_number, cn = sfo_info
            if serial_number in processed_serial_numbers:
                log.debug("duplicate: {} ({})".format(serial_number, cn))
                continue

            processed_serial_numbers[serial_number] = True
            sfo_summary.append({
                "chain_len": chain_len,
                "chain_bytes": chain_bytes,
                "num_sfo": num_sfo,
            })

            if num_sfo == 0 or num_sfo > 5:
                log.debug("{} => {} ({})".format(num_sfo, serial_number, cn))
    return sfo_summary

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main())
