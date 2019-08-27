#!/usr/bin/python

from __future__ import division

import logging
import sys

import numpy as np
import matplotlib.pyplot as plt

def plot_cdf(data, path, xlabel="", title=""):
    linestyle, markerstyle, colorstyle = plotstyle()
    fig, ax = plt.subplots()

    logging.info("Plotting {}".format(path))
    for i, entry in enumerate(data):
        x, label = entry
        ax.plot(sorted(x), np.array(range(len(x))) / len(x),
            ls=linestyle[i],
            color=colorstyle[i],
            marker=markerstyle[i],
            markevery=1 if len(x)<10 else int(len(x)/10),
            label=label,
        )
        logging.info("{} avg: {}".format(label, np.mean(np.array(x))))
        logging.info("{} 50%: {}".format(label, np.percentile(np.array(x), 50)))
        logging.info("{} 90%: {}".format(label, np.percentile(np.array(x), 90)))

    fig.set_size_inches(5,3)
    ax.set_facecolor("#fbfbfb")
    ax.set_xlabel(xlabel, color=[0,0,0,1])
    ax.set_ylabel("cdf", color=[0,0,0,1])
    if data[0][1] is not None:
        plt.legend(facecolor="#f7f7f7")
    plt.grid()
    plt.tight_layout()
    plt.savefig(path)

def plot_data(data, path, xlabel="", ylabel="", title=""):
    linestyle, markerstyle, colorstyle = plotstyle()
    fig, ax = plt.subplots()

    logging.info("Plotting {}".format(path))
    for i, entry in enumerate(data):
        x, y, label = entry
        ax.plot(x, y,
            ls=linestyle[i],
            color=colorstyle[i],
            marker=markerstyle[i],
            markevery=1 if len(x)<10 else int(len(x)/10),
            label=label,
        )

    fig.set_size_inches(5,3)
    ax.set_facecolor("#fbfbfb")
    ax.set_xlabel(xlabel, color=[0,0,0,1])
    ax.set_ylabel(ylabel, color=[0,0,0,1])
    ax.set_title(title)
    if data[0][2] is not None:
        plt.legend(facecolor="#f7f7f7")
    plt.grid()
    plt.tight_layout()
    plt.savefig(path)

def plotstyle():
    '''plotstyle:
    Sets a number of parameters for our graphs, returning line style (ls=),
    marker style (marker=), and color style (color=) to use while plotting.
    '''
    plt.style.use('ggplot')
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['font.size'] = 12
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.facecolor'] = '#fbfbfb'
    plt.grid()
    plt.tight_layout()

    return [":", "--", "-.", "-", "-.", "-", ":", "--"]*5,\
        ['o', 's', 'v', '^', '<', '>', '*', 's', 'p', '*', 'h', 'H', 'D', 'd']*5,\
        ['#d44f7e', '#ffd03d', '#2fb651', '#fb8134', '#7556a2', '#5bb2e5']*5

if __name__ == "__main__":
    logging.critical("no main module")
    sys.exit(1)
