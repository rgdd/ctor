# Timed inclusion queries over Mullvad
This document describes an experimental setup that can be used to determine the
time it takes to query CT logs for inclusion proofs over all Mullvad VPN relays.

## Setup
1. Install Mullvad, see instructions [here](https://mullvad.net/en/help/install-mullvad-app-linux/).
2. Install `python3` and further dependencies using `pip`:
```
$ pip install requests
```
3. Optional: [obtain your own SCT leaf hash data set](https://github.com/rgdd/ctor/tree/master/exp/lh-dl)
and save it as `scthash.json`.

Note: we ran this setup on Ubuntu 18.04.3 LTS.

## Test
```
$ python3 rttct.py -i scthash.json -o output.json -t 10
[INFO] using SCTs from 4 logs
[INFO] downloaded one STH per log
[INFO] stored results: output.json
$ cat output.json
{
  "https://ct.googleapis.com/logs/argon2019/": [
    0.902595,
    0.94427,
	...
  ],
  "https://ct.cloudflare.com/logs/nimbus2019/": [
    0.259553,
    0.241702,
	...
  ],
  "https://sabre.ct.comodo.com/": [
    0.162813,
    0.168694,
	...
  ],
  "https://ct2.digicert-ct.com/log/": [
    0.119027,
    0.118051,
	...
  ]
}
```

## Run
Repeat and instance of the `rttct` module for each Mullvad relay until killed:
```
$ ./main 2>&1 | tee main.log
```
