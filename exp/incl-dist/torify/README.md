# Timed inclusion queries over Tor
This document describes an experimental setup that can be used to determine the
time it takes to query CT logs for inclusion proofs over Tor.

## Setup
1. Install tor, see instructions [here](https://2019.www.torproject.org/docs/debian.html.en).
2. Install `python3` and further dependencies using `pip`:
```
$ pip install requests
```
3. Optional: [obtain your own SCT leaf hash data set](https://github.com/rgdd/ctor/tree/master/exp/lh-dl)
and save it as `scthash.json`.

Note: we ran this setup on Ubuntu 18.04.3 LTS.

## Test
```
$ torify python3 rttct.py -i scthash.json -o output.json -t 10
[INFO] using SCTs from 4 logs
[INFO] downloaded one STH per log
[INFO] stored results: output.json
$ cat output.json
{
  "https://ct.googleapis.com/logs/argon2019/": [
    0.772176,
    1.404443,
	...
  ],
  "https://ct.cloudflare.com/logs/nimbus2019/": [
    0.687733,
    0.737327,
	...
  ],
  "https://sabre.ct.comodo.com/": [
    0.576007,
    0.629665,
	...
  ],
  "https://ct2.digicert-ct.com/log/": [
    0.648923,
    0.602497,
	...
  ]
}
```

## Run
Repeat a torified instance of the `rttct` module until killed:
```
$ sudo ./main 2>&1 | tee main.log
...
```
