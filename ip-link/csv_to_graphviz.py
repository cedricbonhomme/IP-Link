#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""csv_to_graphviz

Charge un fichier CSV et génère un fichier au format DOT pour GraphViz.
"""

import csv


class excel_french(csv.Dialect):
    delimiter = ";"
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("excel_french", excel_french)


def csv_to_graphviz(csv_file, gv_file):
    """Generate a DOT file for GraphViZ from a CSV file."""
    if options.verbose:
        print("Loading CSV file...")
    cr = csv.reader(open(csv_file, "rb"), "excel_french")

    liste_ip, liste = [], []
    for ip in cr:
        liste.append((ip[0], ip[1]))
        if ip[0] not in liste_ip:
            liste_ip.append(ip[0])
        if ip[1] not in liste_ip:
            liste_ip.append(ip[1])

    if options.verbose:
        print("Creating GraphViz DOT file...")
    gv_txt = "digraph G {\n"
    gv_txt += "\tbgcolor=azure;\n"
    gv_txt += "\tranksep=2;\n"
    gv_txt += "\tratio=auto;\n"
    gv_txt += "\tcompound=true;\n"
    gv_txt += "\tnodesep=5;\n"
    gv_txt += "\tnode [shape=box, color=lightblue2, style=filled];\n"
    gv_txt += "\tedge [arrowsize=2, color=gold];\n"
    for ip in liste_ip:
        gv_txt += '"' + ip + '"' + ";\n"

    for ip_src, ip_dst in liste:
        gv_txt += '\t"' + ip_src + '" -> ' + ' "' + ip_dst + '";\n'
    gv_txt += "}"

    if options.verbose:
        print("Writting file.")
    gv = open(gv_file, "w")
    gv.write(gv_txt)
    gv.close()

    if options.verbose:
        print("See the result :")
        print("\tdotty " + gv_file)
        print("\tdot -Tpng -o " + gv_file)


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="csv_file", help="CSV file")
    parser.add_option("-o", "--output", dest="gv_file", help="GraphViz file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(csv_file="./data/ip.csv", gv_file="./data/ip.dot", verbose=True)

    (options, args) = parser.parse_args()

    csv_to_graphviz(options.csv_file, options.gv_file)
