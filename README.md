# Certificate Transparency in Tor
Work in progress

## Motivation
Certificate Transparency (CT) is not supported by Tor Browser.  This means that
any attacker that is able to control a Certificate Authority (CA) can trivially 
Man-in-the-Middle (MitM) arbitrary Tor Browser users, e.g., by operating exit
relays and/or network links.  While this may be detected by various forms of
multi-path probing, such techniques do not scale for _all_ websites.

Adding CT as deployed in Chrome and Safari would be a significant improvement.
However, if the logs are untrusted and attacker-controlled (as envisioned by CT)
an attacker can still mis-issue certificates and associated Signed Certificate
Timestamps (SCTs) without ever merging the logs.  This means that certificate
mis-issuance could go unnoticed unless presented certificate chains and SCTs
are audited for inclusion.

Overall we want a design that enforces CT without trusting the logs.  This is
not only good for Tor, e.g., it could provide a well-audited view of the logs
that other user agents could rely on.

## Challenges and opportunities
Tor's setting differs significantly when compared to normal browsers and the
regular Internet.  For example, Tor Browser's notion of _disk avoidance_ makes
it hard to enforce any inclusion verification:
- Suppose an SCT is newly issued and used for MitM purposes.  If Tor Browser
tried to verify inclusion the log can claim that the associated certificate has
not been merged yet; come back later.  Unfortunately, later means that Tor
Browser is likely shutdown and any state that links the user to a website (such
as an SCT) must be deleted.

On the other hand, Tor provides anonymity guarantees that a regular browser does
not.  There are also thousands of Tor relays that could potentially be used
for CT-auditing purposes, and a consensus that is assumed to be secure.

## High-level overview

### Tor Browser
- Avoid breakage:
use a CT policy which is similar to Chrome and Safari, i.e., accept a presented
certificate chain iff it has enough valid SCTs.

- Probabilistic inclusion verification:
flip a biased coin for each accepted certificate chain.  If heads, sample a
CT-auditing Relay (CTR) uniformly and submit an
	[SCT Feedback Object](https://tools.ietf.org/html/draft-ietf-trans-gossip-05#section-8.1.1)
(SFO) to it in the background on a fresh independent circuit that is closed as
soon as possible.

### CT-auditing relays
Receives sampled SFOs from Tor Browser users, verifying inclusion with regards
to Signed Tree Heads (STHs) that were announced in the Tor consensus.  Should
issues be found, such as a log refusing to resolve an SCT to a given STH, then
one or more 3rd-party CT auditors are contacted.

We are currently considering several CTR designs that defend against different
types of attackers.   Few general details:
- No SFO should be written to disk because it is a liability to store.
- Use stable middle relays as CTRs because there are much capacity and
diversity here.  This comes at the cost of leaking some Tor Browser usage to
operators that do not expose themselves as exit relays.

### 3rd-party CT auditors
Receives SFOs that CTRs could not verify inclusion for, promising to get to the
bottom of any persistent issues.  Ultimately we want the availability of
3rd-party CT auditors to be the weakest link of our design.

### Directory authorities
- Specify the bias of Tor Browser's coin, e.g., order ~1-10% of submitting.
This should be sufficient given that our attacker is _risk-averse_, see
  [threat-model](https://github.com/rgdd/ctor/blob/master/proposals/threat-model.md).
- Specify the CTR criteria, e.g., must be a middle relay and have the stable
flag.
- Announce the Tor network's view of all CT logs that Tor Browser recognizes.
This means that we do not need to worry about split-views _within the Tor
network_.
- Announce 3rd-party CT auditors that can be contacted if log misbehaviour is
suspected.  This is needed because we cannot expect that relay operators know
how to handle CT issues.
