# Balancing relay design
This document describes the balancing relay design proposal.

## Setting and assumptions
- See [overview](https://github.com/rgdd/ctor/blob/master/README.md)
- Each SCT Feedback Object (SFO) contains no more than a single SCT.

## Setup
- Create (empty) buckets `1...n` that store SFO sets.
- Create an (empty) set of known OnionShare addresses.
- Create an (empty) set of SFO-proof pairs.
- Set `mode` to `passive`
- Start API event handlers

## APIs
- [SFO listener](https://tools.ietf.org/html/draft-ietf-trans-gossip-05#section-8.1.4):
CTRs accept SFOs from anyone on well-known addresses.
- OnionShare address listener: CTRs accept OnionShare addresses from other CTRs.
- OnionShare listener: CTRs share their SFO-proof set on request.

### Event handler: SFO API
For each incoming SFO:
1. Return if `mode == active`
2. Return if SFO is in the SFO-proof set
3. For each bucket `b`:
  1. Flip coin with bias `k/n` for heads [k order ~what?]
  2. If tails:
    - continue
  3. Insert received SFO into bucket `b`

### Event handler: OnionShare address API
For an incoming OnionShare address:
1. Store received OnionShare address in the list.

### Event handler: OnionShare connection API
For an incoming OnionShare connection:
1. Submit entire SFO-proof set.

## Core loop
1. Wait [order ~what?] time units or until some bucket is full.
2. Set `mode` to `active`
3. Create circuit and connect to CT log
4. For each SFO in the union of all buffers:
  1. Challenge the log to prove inclusion with regards to the most recent STH
  in the consensus and a timeout [order ~seconds].
  2. On failure:
    - continue
  3. Store SFO-proof pair in the audited set.
5. For each OnionShare address in the list:
  1. Create circuit and connect
  2. For each received SFO-proof pair:
    - Insert it into the audited set.
6. For each sampled CTR `i`, where `i` in `1...n`:
  1. Create circuit and connect
  2. For each SFO in bucket `i` that there is no valid SFO-proof pair for:
    - Submit SFO using a timeout [order ~seconds]
7. Send audit-onionshare for audit status/results to each CTR_i \neq CTR_0
  - Note sure what this is supposed to do
8. Rotate SFO-proof set so that elements older than [order ~MMD] are removed.
9. Empty all buckets.
10. Set `mode` to `passive` and goto step (1).
