#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""sqlite_to_object

Read the data from the base and generate a serialized graph object.

"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/02/05 $"
__copyright__ = (
    "Copyright (c) 2010-2012 Jerome Hussenet, Copyright (c) 2010-2012 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import sqlite3
import pickle


def sqlite_to_object(sqlite_file, obj_file, request_type, parameters):
    """Querys SQLite data base.

    Extracts information (IP/Port source and IP/Port destination) from the SQLite base
    and serialize an object containing the result.
    """
    if options.verbose:
        print("DB connect")
    conn = sqlite3.connect(sqlite_file, isolation_level=None)

    requests = {
        "all": "SELECT ip_src, ip_dst, port_src, port_dst FROM ip_link",
        "number": "SELECT ip_src, ip_dst, port_src, port_dst FROM ip_link LIMIT number",
        "ip": "SELECT ip_src, ip_dst, port_src, port_dst FROM ip_link\
                    WHERE (ip_src = ip1 AND ip_dst = ip2) OR (ip_src = ip2 AND ip_dst = ip1)",
    }

    req = requests[request_type]
    if request_type == "ip":
        (ip1, ip2) = parameters.split(":")
        req = req.replace("ip1", '"' + ip1 + '"')
        req = req.replace("ip2", '"' + ip2 + '"')
    if request_type == "number":
        n = parameters
        req = req.replace("number", n)

    if options.verbose:
        print("Query sent to the base :\n\t" + req)
    liste = conn.execute(req).fetchall()

    dic = {}

    for ip_src, ip_dst, port_src, port_dst in liste:
        # dic[ip_src][ip_dst][port_src][port_dst] = dic.get(ip_src, {}).get(ip_dst, {}).get(port_src, {}).get(port_src, 0)+1
        if ip_src not in dic:
            dic[ip_src] = {}
            dic[ip_src][ip_dst] = {}
            dic[ip_src][ip_dst][port_src] = {}
            dic[ip_src][ip_dst][port_src][port_dst] = 1
        else:
            if ip_dst not in dic[ip_src]:
                dic[ip_src][ip_dst] = {}
                dic[ip_src][ip_dst][port_src] = {}
                dic[ip_src][ip_dst][port_src][port_dst] = 1
            else:
                if port_src not in dic[ip_src][ip_dst]:
                    dic[ip_src][ip_dst][port_src] = {}
                    dic[ip_src][ip_dst][port_src][port_dst] = 1
                else:
                    if port_dst not in dic[ip_src][ip_dst][port_src]:
                        dic[ip_src][ip_dst][port_src][port_dst] = 1
                    else:
                        dic[ip_src][ip_dst][port_src][port_dst] += 1

    conn.close()

    if options.verbose:
        print("Serialization...")
    dic_obj = open(obj_file, "wb")
    pickle.dump(dic, dic_obj)
    dic_obj.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="sqlite_file", help="SQLite base")
    parser.add_option(
        "-o", "--output", dest="obj_file", help="The Python serialized object"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.add_option(
        "-r", "--request", dest="request_type", help="type of the request"
    )
    parser.add_option(
        "-p", "--parameter", dest="parameter", help="The parameter of the request"
    )
    parser.set_defaults(
        sqlite_file="./data/ip.sql",
        obj_file="./data/dic.pyobj",
        request_type="all",
        parameter="",
        verbose=True,
    )

    (options, args) = parser.parse_args()

    if options.request_type != "all" and options.parameter == "":
        parser.error("Request parameter needed")

    sqlite_to_object(
        options.sqlite_file, options.obj_file, options.request_type, options.parameter
    )
