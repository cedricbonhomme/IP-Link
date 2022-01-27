#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_graphviz

Load a serialized object in memory and generate a DOT file for GraphViz.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/03/06 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import pickle


def object_to_graphviz(obj_file, gv_file):
    """Generate a DOT file for GraphViZ."""
    dic_obj = open(obj_file, "rb")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    # collects all IP
    liste_ip = []
    for i in dic_ip:
        if i not in liste_ip:
            liste_ip.append(i)
        for j in list(dic_ip[i].keys()):
            if j not in liste_ip:
                liste_ip.append(j)

    if options.verbose:
        print("Creating GraphViz DOT file...")
    gv_txt = "digraph G {\n"
    gv_txt += "\tbgcolor=azure;\n"
    gv_txt += "\tranksep=10;\n"
    # gv_txt += '\tratio=auto;\n'
    gv_txt += "\tcompound=true;\n"
    # gv_txt += '\tnodesep=5;\n'
    # gv_txt += '\tnode [shape=box, color=lightblue2, style=filled];\n'
    gv_txt += "\tedge [arrowsize=2, color=gold];\n"
    for ip in liste_ip:
        gv_txt += '"' + ip + '"' + ";\n"

    for ip_src in dic_ip:
        for ip_dst in dic_ip[ip_src]:
            gv_txt += (
                '\t"'
                + ip_src
                + '" -> '
                + ' "'
                + ip_dst
                + '" [label = "'
                + str(dic_ip[ip_src][ip_dst])
                + '"];\n'
            )
    gv_txt += "}"

    if options.verbose:
        print("Writting file.")
    gv = open(gv_file, "w")
    gv.write(gv_txt)
    gv.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="gv_file", help="GraphViz file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", gv_file="./data/ip.dot", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_graphviz(options.obj_file, options.gv_file)
