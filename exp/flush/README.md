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

# Network-wide flush
After conducting an attack with a newly issued SFO, it will be spread across
zero or more CTRs.  Once some threshold elapses, e.g., an MMD, auditing can
start because the log must have merged it.  Regardless of if the threshold is an
MMD or less, there will be a window where the attacker knows that the
mis-issued SFO is located at zero or more CTRs but cannot tell where exactly.
One way to avoid detection, then, is to flush _all_ CTRs.  We call this threat a
_network-wide flush_.

## How difficult is it to flush the entire network?
Suppose that each CTR has 1 GiB of memory available for SFO storage.  Further,
the attacker wants 99 per cent certainty that a single MitM attack goes
unnoticed, Tor Browser submits an SFO with 10 per cent chance, and 6 KiB
of bandwidth is used while submitting an SFO to a CTR.

Without any flushing, the attacker has ten per cent chance of failing.  If there
is also a ten per cent chance that a following flush will fail, the complete
likelihood of failure is `0.01 <-- 0.10*0.10`.  As such, the attacker must flush
a single CTR with 90 per cent certainty to have a 99 per cent chance of staying
undetected.

Now suppose that we use stable non-exit Tor relays as CTRs.  According to
[Tor Metrics::Servers](https://metrics.torproject.org/relayflags.html), there
are around 4000 such Tor relays.  From the output of `sim.py`, we know that
433,218 SFO submissions flush a single 1GiB CTR with 90 per cent certainty.
Since the attacker does not know which CTR to flush, a network-wide flush is
necessary.  This requires `1.73B <-- 4000 * 433218` SFO submissions in total.

Unsurprisingly, 1.73B SFOs imply a lot of raw bytes: 9,916 GiB.  To
flush the entire network within an hour, three hours and an MMD, 23.7 Gbps, 7.89
Gbps and 0.99 Gbps bandwidth is required in the respective cases.  While the
required bandwidth is substantial, it is not an immediate impossibility.  For
example, the Tor network advertises roughly 100 Gbps exit bandwidth
as of [February 2020](https://metrics.torproject.org/bandwidth-flags.html).  And
more concerning, it appears that there is enough spare bandwidth available to
conduct such flushing activities.

What did we learn from this example then?  A powerful attacker can likely
conduct a network-wide flush despite a CTR design that attempts to audit SFOs
before their respective MMDs elapsed.  Nevertheless, it should be noted that
network-wide flushes can be detected.  For starters, it will explode the number
of Tor circuits and thus stick out in metrics as an anomaly.  Secondly, and more
reliably, we can rely on [ctor health
statistics](https://github.com/rgdd/ctor/blob/master/proposals/ctor-health.md).

Note that the attacker's job may be a little bit easier in practice, depending
on its powers.  For example, there is a chance that Tor Browser samples an
attacker-controlled CTR and there is not much point flushing your own CTRs.

## To think about
To make a network-wide flush infeasible, we could require that each SFO
submission includes a payload that makes it more bandwidth-expensive.  The idea,
then, is that the attacker's needed bandwidth should exceed the Tor networks
capacity.  For example, this would be the case in the one-hour example above if
each SFO submission was increased by a factor of five-ish.  Of course, this
comes at the price of more overhead as Tor Browser would have to follow the same
submission rules as the attacker.

On another note, the ballpark here is a bit different if the attacker conducts
many MitM attacks that are contingent in time.  As a result, the mis-issued SFO
will likely end up at many different CTRs.  The attacker's network-wide flush
has to succeed on _every_ CTR that holds the problematic SFO, which requires
more work.  For example, if the attacker suspects that `k` CTRs hold the
problematic evidence, the probability that all flushes succeed is `p^k` where
`p` is the per-relay success probability.  The question of how many CTRs the
attacker should expect depends on how many mis-issued SFOs are given to Tor
Browser.

Something not discussed above is the number of necessary circuits.  If there is
anything that prohibits such large amount of light circuits, then that in itself
poses a problem for the attacker (one SFO per circuit is assumed).  When
compared to the number of initial streams in Mani et al., the attacker needs
much more than is otherwise normal behavior.
