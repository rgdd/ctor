#!/usr/bin/python3

import sys
import logging

import numpy as np
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)

plt.style.use('ggplot')
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['font.size'] = 12
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.facecolor'] = '#f5f5f5'

__line_style = [
    ":", "--", "-.", "-", "-.", "-", ":", "--",
]
__marker_style = [
    'o', 's', 'v', '^', '<', '>', '*', 's', 'p', '*', 'h', 'H', 'D', 'd',
]
__color_style = [
    '#d44f7e', '#ffd03d', '#2fb651', '#fb8134', '#7556a2', '#5bb2e5',
]
__text_color = [0,0,0,1]
__legend_bg_color = "#f7f7f7"

def cdf(data, path, xlabel="", title=""):
    fig, ax = __subplots(xlabel, "cdf", title)
    for i, entry in enumerate(data):
        x, label = entry
        ax.plot(sorted(x), np.array(range(len(x)))/len(x),
            ls = __line_style[i % len(__line_style)],
            color = __color_style[i % len(__color_style)],
            marker = __marker_style[i % len(__marker_style)],
            markevery = 1 if len(x)<10 else int(len(x)/10),
            label = label,
        )
    __plt_config(data[0][1] is not None, path)

def plot(data, path, xlabel="", ylabel="", title=""):
    fig, ax = __subplots(xlabel, ylabel, title)
    for i, entry in enumerate(data):
        x, y, label = entry
        ax.plot(x, y,
            ls = __line_style[i % len(__line_style)],
            color = __color_style[i % len(__color_style)],
            marker = __marker_style[i % len(__marker_style)],
            markevery = 1 if len(x)<10 else int(len(x)/10),
            label = label,
        )
    __plt_config(data[0][1] is not None, path)

def __subplots(xlabel, ylabel, title):
    fig, ax = plt.subplots()
    fig.set_size_inches(5,3)
    ax.set_xlabel(xlabel, color=__text_color)
    ax.set_ylabel(ylabel, color=__text_color)
    ax.set_title(title, color=__text_color)
    return fig, ax

def __plt_config(make_legend, path):
    if make_legend:
        plt.legend(facecolor=__legend_bg_color)
    plt.tight_layout()
    plt.grid()
    plt.savefig(path)

if __name__ == "__main__":
    log.critical("no main module")
    sys.exit(1)
