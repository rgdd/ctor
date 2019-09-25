# Secret-bounce relay design
This document describes the secret-bounce relay design proposal. The proposal is
called "secret-bounce" because it should be hard for the attacker to learn where
an SFO is immediately bounced after a client's initial submission. In addition,
the design limits to which CTRs SFOs can be bounced to by other CTRs, preventing
attackers that lack control of a large enough fraction of CTRs in the network
from reliably performing tagging attacks.

The proposal is orthogonal to some other relay designs and therefore incomplete
on its own.

## Overview
As part of Tor's consensus, there is a `shared_random` value generated by the
network, and a list of all relays that support CT, i.e., CTRs. Each CTR has an
identity key, using ed25519. 

When a new version of the consensus is available to a CTR, the CTR uses the new
`shared_random` together with its identity key to determine which CTRs in the
network it is allowed to bounce SFOs to. How this is done can be seen based on
how authentication is done, see below. The CTR maintains a circuit to each other
CTR it's allowed to bounce to, and when a SFO is received from a client flips a
fair coin and forwards/bounces the randomly selected CTR. 

For SFOs forwarded/bounced from other CTRs, the CTR maintains isolated buffers
and follows another relay design for each buffer, e.g.,
[zero-bounce](https://github.com/rgdd/ctor/blob/master/proposals/relay/zero-bounce.md).

That SFOs from different CTRs are isolated to ensure that no tagging is
possible. We might be able to relax this, depending on how parameters are
selected. Depending on the fraction of attacker-controlled CTRs, it might be
possible to conduct network-wide flushes with high certainty.  

## Authenticated SFO API
When a CTR receives a SFO from another CTR (on a dedicated API endpoint), the
CTR authenticates the request as follows:
- input: 
    - one or more SFOs, 
    - a signature `s`, 
    - a `shared_random`, 
    - a sorted list of all CTR fingerprints from the consensus,
    - the requesting CTR's fingerprint

- output: success or error
  
1. get verification key `vk` (ed25519) based on fingerprint
2. verify that `shared_random` is new enough (accept current and prev from
   consensus?)
3. verify signature using `vk` on message `shared_random` with prefix
   `ctor-v0-auth`
4. accept the SFOs iff this relay is one of `N` CTRs whose fingerprint
   immediately follows the value of the signature in the list of CTR
   fingerprints


#### Caveats
- For the above to work, the implementation of ed25519 in tor has to provide
non-malleable signatures. Currently, it does not appear to do so. Therefore, we
need to construct a [Verifiable Random Function
(VRF)](https://tools.ietf.org/id/draft-irtf-cfrg-vrf-04.html). ([Explanation of
the difference between signatures and vrf
here](https://crypto.stackexchange.com/questions/50681/what-is-the-difference-between-signatures-and-vrf).).
We can probably get away with a [weak
VRF](http://www.wisdom.weizmann.ac.il/~zvikab/localpapers/wvrf.pdf), since
`shared_random` is random.
- poor man's VRF: create an ed25519 signature, then sign that signature with a prefix...,
        and use the inner signature?
- FIXME: probably also hash the fingerprints in the list of CTRs, as in rend-spec-v3
- in step 4 above, we could replace using the signature with the identity of the CTR, and then not need a VRF. This has no downside?