#! /usr/local/bin/python
#-*- coding: utf-8 -*-

"""serializedList_to_object

Reads the data from the serialized list object to generate a serialized graph.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/02/22 $"
__copyright__ = "Copyright (c) 2009 Jerome Hussenet, Copyright (c) 2009 Cedric Bonhomme"
__license__ = "Python"

import pickle

def serializedList_to_object(objlist_file, objgraph_file, \
                                request_type, parameter):
    liste_obj = open(objlist_file, "r")
    liste_ip = pickle.load(liste_obj)

    dic_ip = {}
    print "Creating graph object..."
    for tts, ip_src, ip_dst in liste_ip:
        if ip_src not in dic_ip:
            dic_ip[ip_src] = {}
            dic_ip[ip_src][ip_dst] = 1
        else:
            if ip_dst not in dic_ip[ip_src]:
                dic_ip[ip_src][ip_dst] = 1
            else:
                dic_ip[ip_src][ip_dst] += 1

    print "Serialization..."
    dic_obj = open(objgraph_file, "w")
    pickle.dump(dic_ip, dic_obj)
    dic_obj.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="objlist_file",
                    help="Python serialized list object")
    parser.add_option("-o", "--output", dest="objgraph_file",
                    help="Python serialized graph object")
    parser.add_option("-r", "--request", dest="request_type",
                    help="type of the request")
    parser.add_option("-p", "--parameter", dest="parameter",
                    help="parameter of the request")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose",
                    help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(objlist_file = './data/list.pyobj',
                    objgraph_file = './data/dic.pyobj',
                    request_type = 'all',
                    parameter = '',
                    verbose = True)

    (options, args) = parser.parse_args()

    if options.request_type != 'all' and options.parameter == '':
        parser.error("Request parameter needed")

    serializedList_to_object(options.objlist_file, options.objgraph_file,
                    options.request_type, options.parameter)
