#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_gexf

Loads a serialized graph object in memory and generates an input file
for Gephi (GEXF file).
"""

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2015/02/24 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2015 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import pickle
import networkx as nx

G = nx.DiGraph()


def object_to_gexf(obj_file, graph_file):
    """Create the input file for Gephi (GEXF file)."""
    if options.verbose:
        print("Loading objet...")
    dic_obj = open(obj_file, "rb")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("GEXF graph generation...")

    for ip_src in dic_ip:
        for ip_dst in dic_ip[ip_src]:
            G.add_edge(ip_src, ip_dst, weight=dic_ip[ip_src][ip_dst])

    # Freeing memory
    del dic_ip

    if options.verbose:
        print("Saving the graph...")

    nx.write_gexf(G, graph_file)


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option(
        "-o", "--output", dest="graph_file", help="Input file for Gephi (GEXF file)"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", graph_file="./data/ip.gexf", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_gexf(options.obj_file, options.graph_file)
