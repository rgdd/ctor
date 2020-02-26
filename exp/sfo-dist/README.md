# SFO distribution
Here we visit the most popular reddit websites to collect information about
certificate chains and SCTs.

## Environment setup
- Ubuntu Desktop 19.10 running headless in a VM
- Chromium 77: download `chrome-linux.zip` from
[here](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/681090/) and unzip it as a directory named `77`
- Install other dependencies: `apt install xvfb dbus-x11 python3`

## Run
Below we use a small collection of test URLs as an example.  For more details
about the list of reddit URLs, see
[here](https://github.com/pylls/padding-machines-for-tor/tree/master/collect-traces/lists/unmonitored).

```
$ ./collect
[Info] 1 https://example.com
[Info] 2 https://kau.se
[Info] 3 https://no-sct.badssl.com
[Info] done
$
$ ./parse
[Info] done
$
$ ls parsed
1.json  2.json  3.json
$
```

See `cat parse.py | grep '^#'` for a description of the resulting json files.
