#!/usr/bin/env python3

import sys
import logging
import numpy as np

log = logging.getLogger(__name__)

from util import pop_mani_wilsonbrown_et_al as get_website
from util import tor_network_sim_num_sites as num_websites
from util import sfo_dist

from lfucache import lfu_cache
from lfucache.lfu_cache import NotFoundException

class Relay:
    time = 0 # monotonic counter (seconds)
    log_availability = .999 # probability that an inclusion proof succeeds
    next_resolve = 0 # when to resolve next SFO batch (seconds)
    pending = {} # sfo->audit_after - i.e., track what to resolve
    cache = lfu_cache.Cache() # cache that deletes on least frequently used
    cache_size = 0 # current number of entries in the cache
    circuit_count = 0 # number of CT-related circuits
    submitted_sfo_count = 0 # number of submitted SFOs (i.e., received)
    processed_sfo_count = 0 # number of processed SFOs (i.e., goto pending)
    auditor_submissions = 0 # number of SFOs sent to auditor
    cache_hit_count = 0 # number of cache hits
    pending_hit_count = 0 # number of cache hits in the pending SFOs

    def __init__(self, fraction=1/4096, tb_pr=.10, cache_max=2**10):
        self.tb_pr = tb_pr # probability to submit an SFO from Tor Browser
        self.fraction = fraction # how much CT traffic is received on avg
        self.cache_max = cache_max # TODO: docdoc

    def status(self):
        return self.time,\
            self.circuit_count,\
            self.submitted_sfo_count,\
            self.processed_sfo_count,\
            self.cache_hit_count,\
            self.pending_hit_count,\
            self.auditor_submissions,\
            len(self.pending),\
            self.cache_size,

    def tick(self):
        log.debug("=== time is {} ===".format(self.time))
        self.receive()
        if self.time % 600 == 0: # circuit lifetime is 10m
            log.debug("refreshing log connections on a new circuit")
            self.circuit_count += 1
            log.debug("refreshing auditor connection(s) on a new circuit")
            self.circuit_count += 1
        if self.time >= self.next_resolve:
            self.resolve()
        self.time += 1

    def receive(self):
        for _ in range(num_websites()):
            if np.random.random() <= self.fraction:
                for sfo in sfo_dist(get_website()):
                    if np.random.random() <= self.tb_pr:
                        self.process(sfo)

    def process(self, sfo):
        log.debug("processing a received SFO: {}".format(sfo))
        self.circuit_count += 1
        self.submitted_sfo_count += 1
        if self.is_cached(sfo):
            log.debug("cached - nothing to do here!")
            self.cache_hit_count += 1
            return
        if self.is_pending(sfo):
            log.debug("pending - nothing to do here!")
            self.pending_hit_count += 1
            return

        self.processed_sfo_count += 1
        self.add_pending(sfo, self.audit_after())

    def resolve(self):
        num_queries = 0
        for sfo,audit_after in self.pending.copy().items():
            if self.time >= audit_after:
                num_queries += 1
                self.rem_pending(sfo)
                if np.random.random() <= 1-self.log_availability:
                    log.debug("inclusion failed - sending auditor")
                    self.auditor_submissions += 1
                    log.debug("refreshing log connections on a new circuit")
                    self.circuit_count += 1
                    break

                log.debug("inclusion succeeded: {}".format(sfo))
                self.add_cache(sfo)

        self.sleep(num_queries) # simulate when we wake up again
        log.debug("next resolve: {}".format(self.next_resolve))

    def add_pending(self, sfo, audit_after):
        self.pending[sfo] = audit_after

    def rem_pending(self, sfo):
        self.pending.pop(sfo)

    def is_pending(self, sfo):
        return sfo in self.pending

    def add_cache(self, sfo):
        if self.cache_max <= 0:
            return # no cache
        if self.cache_size >= self.cache_max:
            self.cache.delete_lfu()
            self.cache_size -= 1
        self.cache.insert(sfo, True)
        self.cache_size += 1

    def is_cached(self, sfo):
        try:
            return self.cache.access(sfo) == True
        except NotFoundException:
            return False

    def sleep(self, num_queries):
        '''
        Set next resolve time to simulate a sleep.  Assume 500ms for each query
        that we did, and then sample a sleep from [0s,180s] uniformly.

        TODO: motivate 500ms / tune it
        '''
        self.next_resolve += 0.50 * num_queries
        self.next_resolve += np.random.uniform(0,180)

    def audit_after(self):
        '''
        Return an audit_after timestamp by sampling noise from a lognormal
        distribution:
        - "start": ~3m
        - mean/median: ~10m
        - "long tail": ~30m

        Assumptions:
        - All certificates have 90-day life times (think "LE world").  Life
        times are longer in reality, so our simulation may use more memory.
        - Certificates are issued uniformly throughout the day.
        '''
        audit_after = self.time
        if np.random.random() <= 1/90:
            audit_after += np.random.uniform(0,24*3600)
        audit_after += np.random.lognormal(0,.3)*585
        return audit_after

if __name__ == "__main__":
    log.critical("module contains no main")
    sys.exit(1)
