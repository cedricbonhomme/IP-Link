#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_circos

Loads a serialized graph object in memory and generates an input file
for Circos (matrix).
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2009/03/14 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "Python"

import pickle

from collections import Counter


def object_to_circos(obj_file, circos_file):
    """Create the input file for Circos."""
    if options.verbose:
        print("Loading objet...")
    dic_obj = open(obj_file, "rb")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("Searching IP that are source and destination...")
    ip_state = Counter()
    for ip_src in dic_ip:
        if ip_src not in ip_state:
            ip_state[ip_src] += 1
        elif ip_state[ip_src] == 2:
            ip_state[ip_src] += 1

        for ip_dst in dic_ip[ip_src]:
            if ip_dst not in ip_state:
                ip_state[ip_dst] = 2
            elif ip_state[ip_dst] == 1:
                ip_state[ip_dst] += 2

    liste_ip = []
    for ip in ip_state:
        if ip_state[ip] == 3:
            liste_ip.append(ip)

    if options.verbose:
        print("Circos matrix generation...")
    # build the table s/d
    # first dimension : source ip
    # second dimension : destination ip
    # data : relations number
    tab = {}
    for i in liste_ip:
        tab[i] = {}
        for j in dic_ip[i]:
            if ip_state[j] == 3:
                tab[i][j] = dic_ip[i][j]
        tab[i][i] = "-"

    # Freeing memory
    del dic_ip
    del liste_ip
    del ip_state

    if options.verbose:
        print("Saving the matrix...")
    tab_file = open(circos_file, "w")
    s = []
    s.append("ip")
    for i in tab:
        s.append(i)
    tab_file.write("\t".join(s) + "\n")

    for i in tab:
        s = []
        s.append(i)
        for j in tab:
            try:
                s.append(str(tab[i][j]))
            except:
                s.append("0")
        tab_file.write("\t".join(s) + "\n")

    tab_file.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="circos_file", help="Circos file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", circos_file="./data/ip.circos", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_circos(options.obj_file, options.circos_file)
