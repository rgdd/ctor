# Zero-bounce relay design
This document describes the zero-bounce relay design proposal. The proposal is
called "zero-bounce" because no SFOs are bounced to other CTRs at all, only sent
directly to one or more auditors. 

This design is fragile, notably, if identified by the attacker,
DoS/isolating/crashing the CTR is enough to get rid of a problematic SFO. 

For this design, CTRs can operate with a consensus that is as most `C` seconds
old. 

## On new SFO
When a new SFO is sent over a circuit to the CTR's API:
1. Check if at most `m` [order: 1-10] SFOs have already been sent over this
   circuit, otherwise return an error and stop.
2. Verify that the SFO contains necessary SCTs in accordance to Tor's CT policy,
   otherwise return an error and stop.
3. Check the SCT cache using the first (byte order) SCT in the SFO, if hit,
   discard the SFO and stop.
4. Check the SFO buffer, if already there, discard the SFO and stop.
5. Based on the SCT in the current SFO that is associated with the largest
MMD constant, calculate an `audit_after` timestamp as follows:
```
audit_after = now()
if SCT.timestamp + MMD + C > audit_after:
    audit_after = min(SCT.timestamp, audit_after) + MMD + C
audit_after += random_delay()
```
Above, `now()` gets the current time and `min(a,b)` returns the smallest of its
arguments. With `random_delay()` we add a small delay
(order: seconds to few minutes) in case of little load at the relay. Ultimately,
the above code ensures that we wait at most `MMD+C+random_delay()` seconds until
auditing the SCT, regardless of what the (attacker's) SCT timestamp implies.

6. Finally, store the SFO with its `audit_after` timestamp in the SFO buffer.

## Core relay loop
1. Sample a delay [order: ~minute], schedule a timer to continue with step 2
   after the delay.
2. Create dedicated circuits and establish connections to CT logs and one or
   more auditor(s).
3. Loop (until cannot pick any more): randomly pick a SCT from a random SFO in
    the SFO buffer with `audit_after < now()`: 
   1. Send a challenge with the SCT to the relevant CT log, using the STH from
      the latest valid consensus and a sampled `timeout` [order: seconds].
   2. On valid proof, add SFO to cache by caching the first SCT of the SFO,
      remove the SFO from the buffer, and `continue` loop. 
   3. On any other outcome than valid proof (including timeout), immediately
      send the entire SFO to one or more auditor(s), then remove the SFO from
      buffer and `break` the loop.
4. Close all circuits from step 2 and goto step 1.
