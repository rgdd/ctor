# Threat model
This document describes our threat model.

## Assumptions
- The attacker cannot break cryptographic primitives and TLS.
- The attacker is within the threat model of tor and Tor Browser.  For example,
the consensus cannot be forged and there's no global passive attacker that
controls all network links and/or Tor relays.
- All domain owners self or third-party monitor the relevant CT logs with
regards to STHs that were announced in Tor's consensus documents, see
  [directory-authority.md](https://github.com/rgdd/ctor/blob/master/proposals/directory-authority.md).
- Any violation of a CA and/or CT log is an existential threat to it/them, i.e.,
any improperly signed SCT and certificate chain would likely result in removal
from all relevant trust stores.  This leads to a _risk averse_ attacker.

## Goal
If an SCT is issued for a mis-issued certificate and subsequently used to MitM a
_Tor Browser user_ that the attacker does not control, any CT log that violates
(or violated) its MMD will get caught with non-negligible probability given a
security parameter `t`.  In other words, the attacker's goal is to MitM an HTTPS
connection between Tor Browser and a destination server with negligible
probability of _retroactive_ detection.

## Limitations
- Due to Tor Browser's disk avoidance criteria, any inclusion verification must
necessarily be probabilistic.
- It is inevitable to leak _some_ Tor Browser usage, e.g., to CT logs when
querying for inclusion.
- We do not consider the fact that CT logs may put the whole Tor network on
the same split-view.

## Attacker capabilities
1. MitM between Tor exit relays and a given domain.
2. Control a CA that Tor Browser includes in its trust store.
3. Control enough logs to pass Tor Browser's CT policy.  This means that:
	1. valid SCTs can be crafted without merging them into the log(s).
	2. the attacker decides if and when CT queries are responded to.
4. With the restriction of bandwidth and similar resources, use any CT-auditing
Relay (CTR) API to submit large amounts of SFOs.  This may allow:
	1. [flushing](https://ritter.vg/blog-a_bit_on_certificate_transparency_gossip.html):
	force random SFO deletes due to running out of memory.
	2. _tagging_:
	submit unique SFOs so that a CTR holding a problematic SFO can be identified
	if it is audited in the same circuit as a tag.
5. Operate and DoS some, _but not all_, 3rd-party CT auditors that the Tor
project announces.
6. Operate a fraction of Tor relays.
7. Disrupt a fraction of Tor relays:
	1. _isolate_: remove a Tor relay's connectivity.
	2. _restart_: restart a Tor relay so that all volatile memory is lost.
	3. _takeover_: gain access to a Tor relay's state and continue operating it.
8. Correlate a fraction of real-time low-latency interactions between:
   	1. Tor Browser <-> MitM location
   	2. Tor Browser <-> Tor relay
	3. Tor relay <-> Tor relay
	4. Tor relay <-> CT log
9. Access to a Tor Browser zero-day which allows loading, executing and
escalating privileges.

Capabilities (7) and (8) include _roving_, which means that the attacker chooses
an optimal fraction during each epoch _adaptively_.  These capabilities may also
be _probabilistic_, in which case the attacker's actions succeed with
probability `p`.  The time it takes to use a capability should be treated as a
security parameter.  For relay disruption, ~ms is likely conservative while
~seconds may underestimate some attackers.

Note that (9) might be outside of Tor's threat model, but it is valuable to keep
in mind because there are at least two reasons to MitM a Tor Browser session:
traffic inspection and de-anonymization.  It is difficult (nearing impossible) to target a specific user; due to Tor's anonymity, circuit isolation, and HTTPS Everywhere. It is eminently possible to target all users of a given website, by intercepting traffic between that website and all exit nodes. Once traffic interception is achieved (for all users), it becomes trivial to serve an exploit to all users as well as much easier to target an exploit for a given user (either via traffic confirmation observing encrypted traffic of a suspected user or by users identifying themselves to the website.) _It's important to consider (9) because exploitation is a primary reason to MitM Tor Browser HTTPS sessions_.
