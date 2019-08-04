# Single-bounce relay design
This document describes the single-bounce relay design proposal.

For sake of simplicity, assume that each SFO (SCT Feedback Object) consists of a
single SCT and that there's only one CT log. We denote relays that can be used
for CT-related tasks (as per our proposal) as CTRs. Tor Browser sends SFOs with
some probability to a random CTR, closing its connection and circuit ASAP. The
consensus constains a STH to be used for auditing. Relays can operate with a
consensus that is as most `C` seconds old. 

## On new SFO from API
First check the cache, if hit, discard the SFO and stop. Otherwise, calculate an
`audit_after` timestamp as follows:

```
audit_after = now()
if SCT.timestamp+MMD+C > audit_after:
    audit_after = min(SCT.timestamp+MMD+C, audit_after+MMD+C)
audit_after += random_delay()
```

Above, `now()` gets the current time, `min(a,b)` returns the smallest of its
arguments, and `MMD` is a constant. With `random_delay()` we add a small delay
(order: seconds to few minutes) in case of litle load at the relay. Ultimately,
the above code ensures that we wait at most `MMD+C+random_delay()` seconds until
auditing the SCT, regardless of what the (attacker's) SCT timestamp implies.

Finally, store the SFO with its `audit_after` timestamp in the SFO buffer.

## Core relay loop
1. Sample a delay [order: ~minute], schedule a timer to continue with step 2
   after the delay.
2. Create circuits and establish connections: one to CT log, one to random CTR,
   and one or more to auditor(s).
3. Loop (until cannot pick any more): randomly pick a SFO from buffer with
    `audit_after < now()`: 
   1. Send a challenge with SFO to the CT log, using the STH from the latest valid
      consensus and a sampled `timeout` [order: seconds].
   2. On valid proof, add SFO to cache, remove from buffer, `continue` loop. 
   3. On any other outcome than valid proof (including timeout), immediately
      toss a biased coin [order: ~20% auditor(s)], either send SFO to auditor(s)
      or bounce to CTR, then (optional) remove SFO from buffer and `break` loop.
4. Close all circuits from step 2 and goto step 1.
