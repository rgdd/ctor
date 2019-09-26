# Flushing a single CTR
We consider the case where an attacker already filled a CTR's finite SFO
memory.  This means that for each incoming SFO, another SFO must be
[deleted at random](https://ritter.vg/blog-a_bit_on_certificate_transparency_gossip.html).

Given "enough" SFO submissions, an attacker can use this to _flush_ a target SFO
and thus prevent it from being audited.  The number of required submissions
depend on how certain the attacker needs to be that the flush succeeded, as
well as the number of SFOs that can be stored by the CTR.

In `sim.py`, we enumerate different attacker certainties and memory assumptions
to determine what "enough" means in the respective scenarios.

## Deriving the formula used
The formula below is derived from the intuition of sampling with
replacements.  In other words, if the attacker does not sample a target SFO,
some other irrelevant SFO is deleted and replaced by the new submission.

1. Let `N` be the number of stored SFOs.  As such, the probability to sample a
target SFO is `1/N`, and the probability to _not_ sample a target SFO is
`q = 1 - 1/N`.
2. The probability to not sample a target SFO after `k` submissions is `q^k`,
and thus the probability to sample it _at least once_ is `1 - q^k`.
3.  This gives us the following equation:
`Pr["Flush succeeds with k submissions"] = 1 - q^k`
4. Solving for `k` and substituting `q`:
`k = log(1 - Pr["Flush succeeds with k queries"]) / log(1 - 1/N)`

## Generate data
```
$ ./sim.py
[INFO] generating flush data
[INFO] results stored: output.json
$ cat output.json
{
	...
	"0.999": {
		...
		"1073741824": 1299654.1162962604
	}
}
```

As shown above, 1.2M SFO submissions flush a CTR with 1GiB memory and 0.999
certainty.
