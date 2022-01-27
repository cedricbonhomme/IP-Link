#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_d3js_matrix

Loads a serialized graph object in memory and generates an input file
for D3.js.
"""

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2015/02/06 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2015 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import json
import pickle


def object_to_d3js(obj_file, matrix_file):
    """Create the input file for D3.js."""
    if options.verbose:
        print("Loading objet...")
    dic_obj = open(obj_file, "rb")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("D3JS matrix generation...")

    is_node_added = {}
    ip_number = -1

    d3js_json = {}
    d3js_json["nodes"] = []
    d3js_json["links"] = []
    for ip_src in dic_ip:
        if ip_src not in is_node_added:
            d3js_json["nodes"].append({"name": ip_src, "group": 1})
            is_node_added[ip_src] = True
            ip_number += 1
            source_ip_number = ip_number
        for ip_dst in dic_ip[ip_src]:
            if ip_dst not in is_node_added:
                d3js_json["nodes"].append({"name": ip_dst, "group": 2})
                is_node_added[ip_dst] = True
                ip_number += 1

            d3js_json["links"].append(
                {
                    "source": source_ip_number,
                    "target": ip_number,
                    "value": dic_ip[ip_src][ip_dst],
                }
            )

    # Freeing memory
    del dic_ip

    if options.verbose:
        print("Saving the matrix...")

    with open(matrix_file, "w") as outfile:
        json.dump(d3js_json, outfile)


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="matrix_file", help="Input file for D3.js")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", matrix_file="./data/ip.json", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_d3js(options.obj_file, options.matrix_file)
