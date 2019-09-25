#!/usr/bin/python3

import sys
import logging
import argparse
import json
import requests

log = logging.getLogger(__name__)

def main(args):
    lines, err = read(args.input)
    if err is not None:
        log.error(err)
        return 1

    log_metadata, err = get_logs(args.log_metadata_url)
    if err is not None:
        log.error(err)
        return 1

    parsed, err = parse(lines, extract_logs(log_metadata))
    if err is not None:
        log.error(err)
        return 1

    err = write(parsed, args.output)
    if err is not None:
        log.error(err)
        return 1

    return 0

def read(path):
    try:
        with open(path, "r") as f:
            lines = [ line.rstrip("\n") for line in f ]
        log.info("read {} lines from input: {}".format(len(lines), path))
        return lines, None
    except IOError as e:
        return [], "IOError@read() => {}".format(e)

def write(parsed, path):
    try:
        with open(path, "w") as f:
            json.dump({ log: list(parsed[log]) for log in parsed }, f, indent=2)
        log.info("stored json-ecoded results: {}".format(path))
        return None
    except IOError as e:
        return "IOError@write() => {}".format(e)

def parse(lines, ct_logs):
    parsed, it = {}, iter(lines)
    for log_line in it:
        for ct_log in ct_logs:
            name, search_key = ct_log
            if search_key in log_line:
                sct_line = next(it).strip()
                index = sct_line.find("b64__leaf-hash")
                if index < 0:
                    return {}, "missing SCT hash for log: {}".format(name)

                sct_hash = sct_line[index:].split()[1]
                parsed.setdefault(name, set())
                parsed[name].add(sct_hash)
                break # ensure that we don't go to a shorter-match substring
    log.info("parsed SCT hashes from {} logs".format(len(ct_logs)))
    return parsed, None

def get_logs(url):
    try:
        log.info("downloading log metadata from: {}".format(url))
        return requests.get(url).json(), None
    except Exception as e:
        return [], "failed downloading log metadata => {}".format(e)

def extract_logs(log_metadata):
    ct_logs = []
    for operator in log_metadata["operators"]:
        for log in operator["logs"]:
            ct_logs += [ (log["url"], log["description"]) ]
    return sorted(ct_logs, key=lambda ct_log: len(ct_log[1]), reverse=True)

def parse_args():
    parser = argparse.ArgumentParser(description=
        "Creates a json-encoded dictionary of CT logs and SCT hashes "
        "based on the output of running sct_probe, see README.md.",
    )
    parser.add_argument("--input", "-i", type=str,
        default="../data/output.log",
        help="path to the output produced by sct_probe",
    )
    parser.add_argument("--output", "-o", type=str,
        default="../data/output.json",
        help="path to the resulting json file",
    )
    parser.add_argument("--log-metadata-url", "-l", type=str,
        default="https://www.gstatic.com/ct/log_list/v2/all_logs_list.json",
        help="url where to download all known CT logs in json format",
    )
    return parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level = logging.INFO,
    )
    sys.exit(main(parse_args()))
