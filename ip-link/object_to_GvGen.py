#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_GvGen

Generate a DOT file with GvGen.
http://www.picviz.com/sections/opensource/gvgen.html

Example of use:
$ python object_to_GvGen.py -i data/ip.pyobj | dot -Tpng -o graph.png ; gwenview graph.png

"""

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/02/10 $"
__copyright__ = "Copyright (c) 2012 Cedric Bonhomme"
__license__ = "Python"


import pickle

import gvgen


def object_to_GvGen(obj_file):
    """
    Generate a DOT file with GvGen.
    http://www.picviz.com/sections/opensource/gvgen.html
    """
    dic_obj = open(obj_file, "r")
    if options.verbose:
        pass  # print "Loading dictionary..."
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        pass  # print "Creating GvGen object..."

    graph = gvgen.GvGen()
    graph.styleDefaultAppend("color", "lightblue")
    graph.styleDefaultAppend("style", "filled")
    source = graph.newItem("Source")
    destination = graph.newItem("Destination")

    dic_ip_dst = {}

    for ip_src in dic_ip:
        ipsrc = graph.newItem(ip_src, source)
        for ip_dst in dic_ip[ip_src]:
            if ip_dst not in dic_ip_dst:
                ipdst = graph.newItem(ip_dst, destination)
                dic_ip_dst[ip_dst] = ipdst
            else:
                ipdst = dic_ip_dst[ip_dst]
            link = graph.newLink(ipsrc, ipdst)
            graph.propertyAppend(link, "color", "#158510")
            graph.propertyAppend(link, "label", str(dic_ip[ip_src][ip_dst]))

    graph.dot()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(obj_file="./data/dic.pyobj", verbose=True)

    (options, args) = parser.parse_args()

    object_to_GvGen(options.obj_file)
