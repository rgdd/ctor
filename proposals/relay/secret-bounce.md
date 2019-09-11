# Secret-bounce relay design
This document describes the secret-bounce relay design proposal. The proposal
is called "secret-bounce" because it should be hard for the attacker to learn
where an SFO is immediately bounced after a client's initial submission.  As
such, the proposal is orthogonal to some other relay designs and therefore
incomplete alone.

## Preliminaries
Let I be a set of identity strings.  For example:

```
I = {
	"Alice",
	"Bob",
	"Cece",
}
```

Now somebody with a public-key pair `{vk,sk}` should be able to _prove_ that
they sampled a given identity string `i` for an identity set `I` based on some
announced randomness `r` and a secret key `sk`.  In other words, it must be
possible to _verify_ that `i` is the correct value based on the public
parameters and a cryptographic proof.  Without access to the secret key `sk` or
the cryptographic proof that is derived from `sk`, it must be computationally
hard to learn the sampled value which is associated with the public verification
key `vk`.

More concretely, define the following two algorithms:
- `{i,aux} <- Sample(I,n,sk)`: on input of an identity set `I`, nonce `n` and
secret key `sk`, output an image `{i,aux}` where `i` in `I` and `aux` contains
auxiliary info.
- `bool <- Verify(I,n,{i,aux},vk)`: on input of an identity set `I`, a nonce
`n`, an image `{i,aux}` and a public verification key `vk`, output true iff `vk`
proves that `{i,aux} <- Sample(I,n,t)` is a valid image for some secret key `t`
without learning anything about `t`.

Given `I`, `n` and `vk`, it is computationally hard to derive a valid image
`{i,aux}`.

For all `I`, `n` and `sk`, `Pr["Sample(I,n,sk) outputs i"] = 1/I.size()`.

## On new SFO (from anyone)
Setup that runs whenever a new identity set `I` or randomness `r` is available;
`I` represents CTRs and `r` is used to derive a nonce `n`.

1. Close previous bouncing circuit, if any.
2. Derive new bouncing destination by evaluating `Sample(I,n,sk)`.
3. Establish circuit and connect to the sampled bouncing destination, presenting
   `{i,aux}` and `vk` as proof of being a legit bouncing source at this time.

When a new SFO is sent over any circuit to the CTR's API:

3. Bounce SFO to the sampled CTR.

## On new SFO connection (from CTR)
1. Close circuit and stop unless the sender is a legit bouncing source by
   evaluating `Verify(I,n,{i,aux},vk)`.

For each SFO that is sent over the validated circuit to the CTR's API:
- Isolate SFOs that were submitted from different CTRs.
- Follow the logic of another relay design proposal, e.g.,
[single-bounce.md](https://github.com/rgdd/ctor/blob/master/proposals/relay/single-bounce.md).

Note that it is paramount that SFOs from different CTRs are isolated.  For
example, the attacker could schedule tags that will be audited throughout the
next MMD from attacker-controlled CTRs.  And, in practise, there may be multiple
identity sets that are valid at the same time.  By isolating, there's no
opportunity to use this for tagging.

# Limitation
Depending on the fraction of attacker-controlled CTRs, it might be possible to
conduct network-wide flushes with high certainty.  The steps described in
[single-bounce.md](https://github.com/rgdd/ctor/blob/master/proposals/relay/single-bounce.md)
could be applied to make this harder.
