#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""sqlite_to_object

Read the data from the base and generate a serialized graph object.

Allows to filter the content of the base.
Filters can be made on:
 - the timestamp ;
 - destination address ;
 - source address.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2010/12/01 $"
__copyright__ = (
    "Copyright (c) 2009, 2010 Jerome Hussenet, Copyright (c) 2009, 2010 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

from collections import Counter
from collections import defaultdict
from datetime import datetime
from time import mktime

import pickle
import sqlite3

# kinds of requests
requests = {
    "all": "SELECT ip_src, ip_dst FROM ip_link",
    "tts": "SELECT ip_src, ip_dst FROM ip_link WHERE tts >= tts1 AND tts <=  tts2",
    "time": "SELECT ip_src, ip_dst FROM ip_link WHERE tts >= tts1 AND tts <=  tts2",
    "ip_src": "SELECT ip_src, ip_dst FROM ip_link WHERE ip_src = ipsrc",
    "ip_dst": "SELECT ip_src, ip_dst FROM ip_link WHERE ip_dst = ipdst",
}


def sqlite_to_object(sqlite_file, obj_file, request_type, parameter):
    """Querys SQLite data base.

    Extracts information (IP/Port source and IP/Port destination) from the SQLite base
    and serialize an object containing the result.
    """
    if options.verbose:
        print("DB connect")
    conn = sqlite3.connect(sqlite_file, isolation_level=None)

    # Builds the SQLite request
    req = requests[request_type]
    if request_type == "ip_src":
        req = req.replace("ipsrc", '"' + parameter + '"')
    elif request_type == "ip_dst":
        req = req.replace("ipdst", '"' + parameter + '"')
    elif request_type == "time":
        parameters = parameter.split(":")
        t1 = [int(elem) for elem in parameters[0].split("-")]
        t2 = [int(elem) for elem in parameters[1].split("-")]
        begin = datetime(t1[0], t1[1], t1[2], t1[3], t1[4], t1[5])
        end = datetime(t2[0], t2[1], t2[2], t2[3], t2[4], t2[5])

        tts1 = str(mktime(begin.timetuple()) + 1e-6 * begin.microsecond)
        tts2 = str(mktime(end.timetuple()) + 1e-6 * end.microsecond)

        req = req.replace("tts1", tts1)
        req = req.replace("tts2", tts2)
    elif request_type == "tts":
        parameters = parameter.split(":")

        req = req.replace("tts1", parameters[0])
        req = req.replace("tts2", parameters[1])

    if options.verbose:
        print("Query sent to the base :\n\t" + req)
    liste = conn.execute(req).fetchall()

    dic_ip = defaultdict()
    if options.verbose:
        print("Creating object...")
        print("Reading query result...")
    for ip_src, ip_dst in liste:
        if ip_src not in dic_ip:
            dic_ip[ip_src] = Counter()
            dic_ip[ip_src][ip_dst] += 1
        else:
            dic_ip[ip_src][ip_dst] += 1

    if options.verbose:
        print("Serialization...")
    with open(obj_file, "w") as dic_obj:
        pickle.dump(dic_ip, dic_obj)


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="sqlite_file", help="SQLite base")
    parser.add_option(
        "-o", "--output", dest="obj_file", help="The Python serialized object"
    )
    parser.add_option(
        "-r", "--request", dest="request_type", help="type of the request"
    )
    parser.add_option(
        "-p", "--parameter", dest="parameter", help="The parameter of the request"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
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
