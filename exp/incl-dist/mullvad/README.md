# Timed inclusion queries over Mullvad
This document describes an experimental setup that can be used to determine the
time it takes to query CT logs for inclusion proofs over Mullvad VPN.

## Setup
1. Install Mullvad, see instructions [here](https://mullvad.net/en/help/install-mullvad-app-linux/).
2. Install `python3` and further dependencies using `pip`:
```
$ pip install requests
```
3. Optional: [obtain your own SCT leaf hash data set](https://github.com/rgdd/ctor/tree/master/exp/lh-dl)
and save it as `scthash.json`.

Remark: we ran this setup on Ubuntu 18.04.3 LTS.

## Test
```
$ python3 rttct.py -i scthash.json -o output.json -t 10
$ cat output.json
```

## Run
Repeat and instance of the `rttct` module forever until killed:
```
$ ./main 2>&1 | tee main.log
```
