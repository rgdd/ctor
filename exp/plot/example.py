#!/usr/bin/python

import sys
import plotter

def main():
    data = [
        ([1,2,3,4,5, 1,2,3,4, 1,2,3, 1,2, 1], "5...1, 4...1, ..."),
        ([1,2,3,4, 1,2,3, 1,2, 1], "4...1, 3...1, ..."),
        ([1,2,3,4,5,6,7,8,9,10], "1...10"),
    ]
    plotter.cdf(data, "example.pdf", xlabel="xlabel text", title="title text")

if __name__ == "__main__":
    sys.exit(main())
