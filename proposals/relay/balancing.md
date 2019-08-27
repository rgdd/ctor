# balancing relay design
This document describes the balancing relay design proposal.

--------------------------------------
Pseudo-spec 'cause I don't know what I'm doing, basing off terminology
and design of Tobias's below.

Upon firing up or after audit is conducted:

Set to passive_receive mode

Calculate `audit_after` timestamp as below, except global, not per SCT.

Allow inbound connections on API from any client or CTR 
[Option: limit the number of CTR connections as per capacity.]

Receive SFOs on API, discard if duplicate.
Receive onionshare identifiers on API from other CTRs.
[onionshare identifiers provide a unique onionshare address
at which a CTR will make available the audit results it has
recently obtained, e.g., since 2*MMD]


Create n+1 SFO buckets
Upon receiving an SFO, CTR_0 samples randomness (flips weighted n+1 sided coin
k times, discarding repeats).
place the SFO in each of k chosen buckets of the n+1 buckets.
[Option: flip weighted coin n+1 times and place SFO in any bucket
that comes up heads.]


When audit time comes, [or optionally if resources are depleted below
threshold]. 

Set to active mode

As close to simultaneously as feasible:
Start ignoring any inbound SFOs
Connect to log and make audit request for SFOs received since last
  setting to passive mode. 
Connect to any stored onionshare CTRs and retrieve audit results from them.
[Option: Send canary-onionshare to all inbound connected CTRs.]
Close all inbound connections and clear any related memory of them.

Process log response as appropriate.
Process any onionshare results as appropriate.
Combine.

CTR_0 opens n connections to other CTRs chosen randomly (CTR_1, ..., CTR_n)
Send contents of buckets to each, subject to audit results.
Send audit-onionshare for audit status/results to each CTR_i \neq CTR_0

[Options: these are 
                      normal Tor circuit connections
                      normal Tor connections with everything forgotten
                        ASAP except ports, symmetric keys, etc.
                      onion-service connections]

[Option: This assumes it is not feasible for adversary to pop a CTR
upon seeing a tagged/identifiable log or onionshare request
before it has sent its buckets. If that is not conservative enough,
then send the buckets before making the log request or integrating
audit/onionshare results, which should then only be shared 
via onionshare addresses]

Close all existing CTR connections.

Set to passive-receive mode.

end *Notes cause I don't know what I'm doing*
--------------------------------------

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
