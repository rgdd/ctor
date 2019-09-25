# SCT leaf-hashes
This document describes how to collect an SCT leaf-hash data set.

## Setup
1. Install `go`, `wget`, `unzip`, `python3` and `requests` using `pip`.
2. Make a new clone of [certificate-transparency-go](https://github.com/google/certificate-transparency-go):

```
$ go get github.com/google/certificate-transparency-go
$ cd $GOPATH/src/github.com/google/certificate-transparency-go
```

3. Apply the patch described in `log-sct-leaf-hash.patch`:

```
$ git apply /path/to/log-sct-leaf-hash.patch
```

4. Build `ctutil/sctcheck` and test:

```
$ cd ctutil/sctcheck
$ go build
$ ./sctcheck --logtostderr https://example.com
I0921 17:43:26.554469   33237 sctcheck.go:168] Retrieve certificate chain from TLS connection to "example.com:443"
I0921 17:43:26.933094   33237 sctcheck.go:181] Found chain of length 3
E0921 17:43:26.933675   33237 sctcheck.go:82] Found 0 external SCTs for "https://example.com", of which 0 were validated
I0921 17:43:26.933897   33237 sctcheck.go:226] Examine embedded SCT[0] with timestamp: 1543440012614 (2018-11-28 22:20:12.614 +0100 CET) from logID: a4b90990b418581487bb13a2cc67700a3c359804f91bdfb8e377cd0ec80ddc10
I0921 17:43:26.934006   33237 sctcheck.go:239] Validate embedded SCT[0] against log "Google 'Pilot' log"...
I0921 17:43:26.934389   33237 sctcheck.go:244] Validate embedded SCT[0] against log "Google 'Pilot' log"... validated
I0921 17:43:26.934410   33237 sctcheck.go:248] Check embedded SCT[0] inclusion against log "Google 'Pilot' log"...
I0921 17:43:27.895004   33237 serialization.go:240] b64__leaf-hash %sDHKtWAPA2cLntE4rNKEBTFeqLppfDZ2bO7vWTsBi95w=
...
```

As shown on the last line before truncating the output, you should see a
base64-encoded leaf hash.  This is the result of applying our SCT leaf-hash
patch, which is needed to collect SCT leaf-hashes using `ctutil/sctcheck`.

## Create SCT leaf hash data set
1. Run the following from the `src/` directory:

```
$ ./sct_probe && ./parse.py
```

This will create an SCT leaf hash data set in the top-most `data/` directory
based on the `k` most popular Alexa domains.  The data set is json-encoded as
a dictionary, where each key is a CT log URL and the associated value a list
of SCT leaf hashes in base64.  Example output:

```
$ cat ../data/output.json
{
  "https://ct.googleapis.com/logs/argon2019/": [
    "89gSHWNxYz5+Hvb0FCZaiZ32scXsHecZiCANSH8aiAU="
  ],
  "https://ct.cloudflare.com/logs/nimbus2019/": [
    "2bNmW4cbEF0PDEt2us1AQhOF6rZyIS9ZXQB+Twpe6W8="
  ]
}
```

## Optional: proof-by-leaf-hash query
1. Obtain an STH:

```
$ curl -G https://ct.cloudflare.com/logs/nimbus2019/ct/v1/get-sth
{
	"tree_size": 475036812,
	"timestamp": 1569256678879,
	"sha256_root_hash": "xuZ7HjWVyKPGXb3DDJy20i0Z1oEObs/Jva4t5xljUlk=",
	"tree_head_signature": "BAMARjBEAiBmPHWg6kY9Gl4J/QkH6p87nVi4wdDZKIKe9M+F+JkDJQIgZ0yK4fzTKAOE2RNEMkL2l3Hzl07Qe30hPJyj8fyUnFc="
}
```

2. Query for an inclusion proof based on the tree size and the collected leaf
hash:
```
$ curl -G https://ct.cloudflare.com/logs/nimbus2019/ct/v1/get-proof-by-hash --data-urlencode 'hash=2bNmW4cbEF0PDEt2us1AQhOF6rZyIS9ZXQB+Twpe6W8=' --data-urlencode 'tree_size=475036812'
{
	"leaf_index": 450063887,
	"audit_path": [ ... ]
}
```

Note that all SCT leaf-hashes has already been verified by `ctutil/sctcheck`
while collecting the data set.
