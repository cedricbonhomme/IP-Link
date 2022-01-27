#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_csv

Loads a serialized graph object in memory and generates a CSV file.

CSV file format:
 - source_ip;destination_ip;count
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/02/19 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import os
import sys

import csv
import pickle


class excel_french(csv.Dialect):
    delimiter = ";"
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("excel_french", excel_french)


def object_to_csv(obj_file, csv_file):
    """Generate CSV file."""
    dic_obj = open(obj_file, "rb")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    c = csv.writer(open(csv_file, "w"), "excel_french")

    if options.verbose:
        print("Writting CSV file...")
    for ip_src in dic_ip:
        for ip_dst in dic_ip[ip_src]:
            c.writerow([ip_src, ip_dst, dic_ip[ip_src][ip_dst]])


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="csv_file", help="CSV file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", csv_file="./data/ip.csv", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_csv(options.obj_file, options.csv_file)
