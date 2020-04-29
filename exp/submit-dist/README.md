# Submit bytes distribution
Here we repeatedly HTTP POST `n` bytes over a wide variety of Tor circuits to an
HTTP server that acknowledges the number of received bytes.  By measuring the
time it takes, we get an understanding of how quickly an SFO may be pushed from
its current location to the next (e.g., Tor Browser to CTR, or CTR to Auditor).

## Environment setup
- Server runs on Ubuntu / Arch.  Needs `python3`.
- Client runs on Ubuntu / Arch.  Needs `curl` and `tor`

Set `UseEntryGuards 0` in `/etc/tor/torrc` on the client side to be sure that a
new guard is selected for each measurement.  Might be redundant though, as we
also wipe all tor state in `/var/lib/tor/state`.

## Start the server
```
$ ./server -h
usage: server.py [-h] [--ip IP] [--port PORT]

Server that echos POSTed length

optional arguments:
  -h, --help            show this help message and exit
    --ip IP, -i IP        Server IP address
	  --port PORT, -p PORT  Server port
$
$
$ ./server.py --ip 127.0.0.1 --port 8000
[INFO] Listening on 127.0.0.1:8000
127.0.0.1 - - [29/Apr/2020 11:22:42] "POST / HTTP/1.1" 200 -
...
```
## Test client once using 32-byte submissions
```
$ env CTOR_SUBMIT_BYTES=32 CTOR_SERVER_IP=127.0.0.1 CTOR_SERVER_PORT=8000 ./client
&& echo ""
32
$
```

## Run timed client repeatedly over Tor
Note that this requires that the server listens on a public IP address.
Configure it at the top of `main` in the `export` statements.
```
$ sudo ./main 2>&1 | tee main.log
[Info] press ctrl+c to quit
[Info] restarted tor
[Info] measurement succeeded
...
```
Each data point is stored on a separate line as follows:
`start-time` `stop-time`.  If there is no timely acknowledgement
from the server, the `stop-time` is set to `-1`.

The resulting output file is stored in the `data` folder.
