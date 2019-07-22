#!/usr/bin/python

import sys
import logging

from os import listdir
from plotstyle import plot_data

def main():
    try:
        plot_mem("data/mem", "img")
        plot_disk("data/disk", "img")
        return 0
    except:
        logging.error("need data/mem, data/disk, and img/ to run")
        return 1

def plot_mem(idir, odir):
    to_plot = []
    for pr,data in load(idir).items():
        to_plot.append((
            [ d[0]/(1024**2) for d in data],
            [ d[1]/1000 for d in data ],
            pr,
        ))
    plot_data(sorted(to_plot, key=lambda x: float(x[2]), reverse=True),
        path="/".join((odir, "ram"))+".pdf",
        xlabel="memory (MiB)",
        ylabel="number of queries (k)",
        title="Probability to succeed with flush",
    )

def plot_disk(idir, odir):
    to_plot = []
    for pr,data in load(idir).items():
        to_plot.append((
            [ d[0]/(1024**3) for d in data],
            [ d[1]/(10**6) for d in data ],
            pr,
        ))
    plot_data(sorted(to_plot, key=lambda x: float(x[2]), reverse=True),
        path="/".join((odir, "disk"))+".pdf",
        xlabel="disk (GiB)",
        ylabel="number of queries (M)",
        title="Probability to succeed with flush",
    )

def load(path):
    data = {}
    for pr in listdir(path):
        data[pr] = []
        with open("/".join((path, pr))) as fp:
            for line in fp:
                size, queries = line.split()
                data[pr].append( [ int(size), float(queries) ])
    return data

if __name__ == "__main__":
    sys.exit(main())
