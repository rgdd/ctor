# Directory authority
This document describes what CT auditors should do while interacting with CTRs.

## Setup
- `Snapshots` is a key-value store that maps a log to a list of STHs.
- `Resolved` contains SFOs that are either verified or scheduled for manual
investigation.
- `Pending` contains SFOs that have yet to be verified for inclusion.
- `Report` is a key-value store that maps a CTR to a rolling window of report
statistics.  Each list-value is composed of the following three-tuple:
	- `timestamp`
	- `invalid_sfo_count`
	- `valid_sfo_count`

## On new incoming circuit
1. Close circuit unless the submitter can prove it is a CTR.
2. `Report[CTR] += [ (now(), 0, 0) ]`
3. For each SFO that was submitted on a well-known address:
	1. If invalid SFO signature(s):
		- `Report[CTR].last[1] += 1`
		- Continue
	2. If SFO not in `Resolved` and SFO not in `Pending`:
		- Insert `(SFO, now())` into `Pending`
	3. `Report[CTR].last[2] += 1`

## Repeat periodically
1. Until there is no newer Tor consensus:
	1. Download and verify next Tor consensus
	2. For each announced STH:
		- Verify signature for `log`
		- Insert STH into `Snapshots[log]`
	3. Verify that newly added STHs are consistent
		- Log error if any problem persists more than an MMD
2. Establish connections to all CT logs.
3. For each `(SFO, timestamp)` in `Pending`:
	1. Challenge `log` to prove inclusion with regards to the first STH
	in `Snapshot[log]` that exceeds `SCT.timestamp + MMD`.
		- Timeout after [~order seconds]
	2. If resolve failure and `timestamp+MMD < now()`:
		- continue
	3. Remove `(SFO, timestamp)` from `Pending`
	4. Insert SFO (or representation thereof) into `Resolved`
	5. If resolve failure:
		- Error: `log` ignored `SFO` since `timestamp`, please investigate.
4. Analyze `Report` statistics for each CTR:
	- Are individual relays reporting invalid SFOs or more than expected?
	- How many CTRs are experiencing resolve failures at this moment?

The purpose of step#4 is to notice both CTR abuse and if any CTR is being
ignored by the logs.  For example, if all CTRs suddenly start submitting SFOs to
the announced auditors that would likely indicate that a log is down.
