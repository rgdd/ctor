#!/usr/bin/env python3

import sys
import math
import numpy as np
import logging

log = logging.getLogger(__name__)


def pop_mani_wilsonbrown_et_al():
    """
    Returns a random website visit.

    This is an approximation of the observed distribution by Mani and
    Wilson-Brown et al. in "Understanding Tor Usage with Privacy-Preserving
    Measurement", Figure 2.
    """
    x = np.random.random() # uniform [0,1), slight bias towards Alexa sites
    if x < 0.401:
        return 0
    if x < 0.401+0.084: # websites (0,10]
      return np.random.randint(0, 10)+1
    if x < 0.401+0.084+0.051: # websites (10,100]
      return np.random.randint(10,100)+1
    if x < 0.401+0.084+0.051+0.062: # websites (100,1k]
      return np.random.randint(100,1000)+1
    if x < 0.401+0.084+0.051+0.062+0.043: # websites (1k,10k]
      return np.random.randint(1000, 10*1000)+1
    if x < 0.401+0.084+0.051+0.062+0.043+0.077: # websites (10k,100k]
      return np.random.randint(10*1000, 100*1000)+1
    if x < 0.401+0.084+0.051+0.062+0.043+0.077+0.07: # websites (100k,1m]
        return np.random.randint(100*1000, 1000*1000)+1
    return np.random.randint(1000*1000, 100*1000*1000)+1 # (1m, 100m]

def tor_network_sim_num_sites(ms=1000):
    """
    Returns how many new websites were visited over Tor in x ms?.

    This is based on 140M websites/24h by Mani et al., the upper bound if a 95%
    confidence interval for inferred website visits in early 2018 for the entire
    Tor network. 
    """
    return int(math.ceil(140*1000*1000 / (24*60*60*1000) * ms))

def sfo_dist(website):
    return [ (website,i) for i in range(32) ] # TODO: accurate sfo distribution

if __name__ == "__main__":
    log.critical("module contains no main")
    sys.exit(1)
