# Threat model
This document describes what might go into our threat model.  Some attacker
capabilities are stronger than others.  The idea is to consider designs and
their trade-offs: security/privacy/performance/complexity.

## Assumptions
- The attacker cannot break cryptographic primitives and TLS.
- The attacker is within the threat model of tor and Tor Browser.  For example,
the consensus cannot be forged and there's no global passive attacker that
controls all network links and/or Tor relays.
- All domain owners self or third-party monitor the relevant CT logs with
regards to STHs that were announced in Tor's consensus documents.
- Any violation of a CA and/or CT log is an existential threat to it/them, i.e.,
any improperly signed SCT and certificate chain would likely result in removal
from all relevant trust stores.  This leads to a _risk averse_ attacker.

## Goal
If an SCT is issued for a mis-issued certificate and used to MitM a _Tor
Browser user_, any CT log that violates (or violated) its MMD will get caught
with non-negligible probability given a security parameter `t`.  In other words,
the attacker's goal is to MitM an HTTPS connection between Tor Browser and a
destination server with negligible probability of _retroactive_ detection.

## Limitations
- Due to Tor Browser's disk avoidance criteria, any inclusion verification must
necessarily be probabilistic.
- It is inevitable to leak _some_ Tor Browser usage, e.g., to CT logs when
querying for inclusion.
- We do not consider the fact that CT logs may put the whole Tor network on
the same split-view.

## Attacker capabilities
The fractions below refer to the number of Tor relays, total exit bandwidth,
or any other option/combination that provides the largest value to the
attacker.  No fraction can be too large since that would break Tor, but they
may either be _static_ as in a fixed set of relays or _dynamic_ by modelling a
roving attacker that chooses relay sets adaptively in epochs (inapplicable for
operating Tor relays).  The time it takes to execute a given exploit is a
security parameter, where zero time units would be the most conservative choice.
In practise ~ms is likely too unreliable for a risk averse attacker, while more
than a few seconds may underestimate relevant attackers.

1. Operate a fraction of Tor relays.
2. Flood a fraction of CT-auditing Relays (CTRs) with large amounts of SCT
Feedback Object (SFO) submissions, using nearly all available bandwidth for the
respective CTRs.  This may allow:
	1. [flushing](https://ritter.vg/blog-a_bit_on_certificate_transparency_gossip.html):
	force random SFO deletes due to running out of memory.
	2. _tagging_:
	submit unique SFOs so that a CTR holding a problematic SFO can be identified
	if it is audited in the same circuit as a tag.
3. Although somewhat related to flooding, DoS a fraction of Tor relays:
	1. _slowpoke_: slow down a Tor relay so that at most `k` bandwidth-limited
	(order~KiB) connections can be established before darkness.
	2. _darkness_: take away a relay's connectivity.
4. Pop a fraction of Tor relays:
	1. _crash_: force an abrupt Tor relay restart so that all volatile memory
	is lost.
	2. _takeover_: gain access to a Tor relay's state and continue operating it
	until the end of an epoch.
5. Flood/DoS/Pop a fraction of 3rd-party CT auditors that were announced by the
Tor project.
6. MitM between Tor's exit relays and a victim's domain.
7. Control a CA that Tor Browser includes in its trust store.
8. Control enough logs to pass Tor Browser's CT policy.  This means that:
	1. valid SCTs can be crafted without merging them into the log(s).
	2. the attacker decides if and when CT queries are responded to.
9. Access to a Tor Browser zero-day which allows loading, executing and
escalating privileges.

Strictly speaking (9) might be outside of Tor's threat model, but it is valuable
to keep in mind because there are at least two reasons to MitM a Tor Browser
session: traffic inspection and de-anonymization.  The latter can likely be
achieved with a Tor Browser zero-day, but having such an exploit load for users
that visit a victim's domain would require an HTTPS MitM for a significant
amount of websites; e.g., due to HTTPS everywhere and because users are
anonymous and cannot be targeted via email.  In other words, _by not considering
(9) we would neglect many incentives to MitM Tor Browser HTTPS sessions_.
