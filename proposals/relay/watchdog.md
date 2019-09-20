# Watchdog relay design
This document describes the watchdog relay design proposal.  The proposal
is called "watchdog" because each CTR selects another CTR to act as its
watchdog while auditing:
	_before_ an SFO is queried for inclusion, send it to the selected watchdog
	and signal on success afterwards.  Unless there is a timely success signal,
	the SFO in question is reported to a third-party auditor by the watchdog.

## On new SFO
Follow the steps described in [zero-bounce](https://github.com/rgdd/ctor/blob/master/proposals/relay/zero-bounce.md).

## On new watchdog circuit
1. Create dedicated circuit(s) and establish connection(s) to at least one
auditor.
2. Let `curr_time, prev_time = INT_MAX, INT_MAX`
3. Let `curr_sfo, prev_sfo = None, None`
4. For each received `SFO` and on closed connection (in which `SFO=None`):
	1. Let `prev_time, curr_time = curr_time, now()`
	2. Let `prev_sfo, curr_sfo = curr_sfo, SFO`
	3. Continue if `curr_time-prev_time < 0`
	4. Continue if `curr_time-prev_time < [order ~seconds]`
	5. Report `prev_sfo` to auditor
	6. Stop if `curr_sfo` is `None`
5. Close all circuits from step 2.

## Core relay loop
1. Sample a delay [order: ~minute], schedule a timer to continue with step 2
   after the delay.
2. Create dedicated circuits and establish connections to CT logs and a sampled
   watchdog.
3. Loop (until cannot pick any more): randomly pick a SCT from a random SFO in
    the SFO buffer with `audit_after < now()`: 
   1. Send SFO to the selected watchdog.
   2. Send a challenge with the SCT to the relevant CT log, using the STH from
      the latest valid consensus and a sampled `timeout` [order: seconds].
   3. On valid proof, add SFO to cache by caching the first SCT of the SFO,
      remove the SFO from the buffer, and `continue` loop. 
   4. On any other outcome than valid proof (including timeout), remove SFO
      from buffer, wait [order ~seconds], and then `break` the loop.
4. Close all circuits from step 2 and goto step 1.
