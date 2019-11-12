# Timed inclusion queries over Tor
This document describes an experimental setup that can be used to determine the
time it takes to query CT logs for inclusion proofs over Tor.

TODO: test instructions and add overview

## Overview
docdoc

## Setup
1. Create an experiment directory and clone `exitmap`:
```
$ mkdir ctor
$ git clone git@github.com:NullHypothesis/exitmap.git
$ cd exitmap
```
2. Install `python2` and further dependencies using `pip`:
```
$ pip install -r requirements.txt
$ pip install requests
```
3. Register `rttct` as an exitmap module:
```
$ cp /path/to/rttct.py src/modules/
```
4. Optional: [obtain your own SCT leaf hash data set](https://github.com/rgdd/ctor/tree/master/exp/lh-dl)
and save it as `ctor/scthash.json`.

## Test
1. Build full circuits to Swedish exit relays and query the logs:
```
$ cd ctor
$ ./exitmap/bin/exitmap --country SE --analysis-dir $pwd/data --tor-dir $pwd/tmp rttct
...
```

If the bootstrap phase gets stuck: remove `tmp` and try again.

2. Example output:
```
$ ls -l data
...
$ cat data/<fpr>
...
```

## Run experiment
1. Repeat an instance of the `rttct` module forever until killed:
```
$ cd ctor
$ ./probe 2>&1 | tee output.log
```

Note that:
- You need `output.log` because it is used by `probe`, i.e., logging is not
optional.
- Collected data can be found in `ctor/data`.
