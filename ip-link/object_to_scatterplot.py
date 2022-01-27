#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_scatterplot

Load a serialized object in memory and generate input files for ploticus.
Then call ploticus to create the png file
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/03/01 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import subprocess
import pickle


def object_to_scatterplot(obj_file, scatter_folder):
    """Generate a scatter plot graph."""
    dic_obj = open(obj_file, "rb")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    dic_l = {}
    for i in dic_ip:
        if not str(i) in dic_l:
            dic_l[str(i)] = 0
        for j in dic_ip[i]:
            if not str(j) in dic_l:
                dic_l[str(j)] = 0

    # Generation of the configuration file for ploticus
    if options.verbose:
        print("Creating ploticus categories file")
    cat_f = open("./scatterplot/cat.inc", "w")
    for i in dic_l:
        cat_f.write(i + "\n")
    cat_f.close()

    # Generation of the data file for ploticus
    if options.verbose:
        print("Creating ploticus data file")
    data_f = open("./scatterplot/data.inc", "w")
    for s in dic_ip:
        for d in dic_ip[s]:
            data_f.write(s + " " + d + " " + str(dic_ip[s][d]) + "\n")
    data_f.close()

    # Call ploticus in order to generate the scatterplot
    cmd = [
        "ploticus",
        "-o",
        scatter_folder + "scatterplot.png",
        "-png",
        "./scatterplot/scatterplot",
        "-csmap",
        "-maxproclines",
    ]
    if options.verbose:
        print("Command to execute :")
        print("\t" + " ".join(cmd))
    # ploticus outputs
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # stdout contains the areas of the HTML shape
    (stdout, stderr) = p.communicate()
    if options.verbose:
        if stderr:
            print("Problem(s) :")
            print(stderr)

    # creating the HTML map
    html = '<!DOCTYPE html>\n<html lang="en-US">\n<head>'
    html += '\n<meta charset="utf-8" />\n<title>IP-Link -- Scatterplot</title>\n</head>\n<body>'
    html += '\n<img src="scatterplot.png" usemap="#map1">'
    html += '\n<map name="map1">\n'
    html += stdout.decode()
    html += "\n</map>"
    html += "\n</body>\n</html>"

    if options.verbose:
        print("Creating HTML map")
    html_file = open(scatter_folder + "index.html", "w")
    html_file.write(html)
    html_file.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option(
        "-o",
        "--output",
        dest="scatter_folder",
        help="Output where the HTML file and the scatterplot will be generated.",
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", scatter_folder="./scatterplot/", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_scatterplot(options.obj_file, options.scatter_folder)
