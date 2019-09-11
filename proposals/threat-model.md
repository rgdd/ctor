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
8. Access to a Tor Browser zero-day which allows loading, executing and
escalating privileges.

Capability (7) includes _roving_, which means that the attacker chooses an
optimal fraction during each epoch _adaptively_.  This capability may also be
_probabilistic_, in which case the attacker's action succeeds with probability
`p`.  The time it takes to disrupt a relay should be treated as a security
parameter, where ~ms is likely conservative while ~seconds may underestimate
some attackers.

Note that (8) might be outside of Tor's threat model, but it is valuable to keep
in mind because there are at least two reasons to MitM a Tor Browser session:
traffic inspection and de-anonymization.  The latter can likely be achieved with
a Tor Browser zero-day, but having such an exploit load for users that visit a
given domain would require an HTTPS MitM for a significant amount of websites;
e.g., due to HTTPS everywhere and because users are anonymous and therefore
harder to target.  In other words, _by not considering (8) we would neglect many
incentives to MitM Tor Browser HTTPS sessions_.
