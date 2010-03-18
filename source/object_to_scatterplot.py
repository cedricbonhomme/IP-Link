#!/usr/bin/python
#-*- coding: utf-8 -*-

"""object_to_scatterplot

Load a serialized object in memory and generate input files for ploticus.
Then call ploticus to create the png file
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/03/01 $"
__copyright__ = "Copyright (c) 2009 Jerome Hussenet, Copyright (c) 2009 Cedric Bonhomme"
__license__ = "Python"

import os
import sys
import pickle

def object_to_scatterplot(obj_file, scatter_file):
    """Generate a scatter plot graph.
    """
    dic_obj = open(obj_file, "r")
    if options.verbose:
        print "Loading dictionary..."
    dic_ip = pickle.load(dic_obj)

    dic_l = {}
    for i in dic_ip:
        if not str(i) in dic_l:
            dic_l[str(i)] = 0
        for j in dic_ip[i]:
            if not str(j) in dic_l:
                dic_l[str(j)] = 0

    if options.verbose:
        print "Creating ploticus categories file"
    cat_f = open("./scatterplot/cat.inc", "w")
    for i in dic_l:
        cat_f.write(i + "\n")
    cat_f.close()

    if options.verbose:
        print "Creating ploticus data file"
    data_f = open("./scatterplot/data.inc", "w")
    for s in dic_ip:
        for d in dic_ip[s]:
            data_f.write(s+" "+d+" "+str(dic_ip[s][d])+"\n")
    data_f.close()


    ploticus = '\tploticus -o ./scatterplot/scatterplot.png -png ./scatterplot/scatterplot -csmap -maxproclines'
    if options.verbose:
        print "Command to execute :"
        print ploticus
    # ploticus outputs
    (child_stdin, child_stdout, child_stderr) = os.popen3(ploticus)
    stderr = child_stderr.readlines()
    stdout = child_stdout.readlines()
    child_stdin.close()
    child_stdout.close()
    child_stderr.close()

    if options.verbose:
        if stderr != []:
            print "Problem(s) :"
            print "\n".join(stderr)

    # creating the HTML map
    html = '<html>\n<head>\n<title>IP-Link -- Scatterplot</tile>\n</head>\n<body>'
    html += '\n<map name="map1">\n'
    for area_shape in stdout:
        html += "\t" + area_shape + "\n"
    html += '</map>\n<img src="scatterplot.png" usemap="#map1">'
    html += '\n</body>\n</html>'

    if options.verbose:
        print "Creating HTML map"
    html_file = open(scatter_file, "w")
    html_file.write(html)
    html_file.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file",
                    help="Python serialized object")
    parser.add_option("-o", "--output", dest="scatter_file",
                    help="Scatter plot HTML map file")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose",
                    help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(obj_file = './data/dic.pyobj',
                    scatter_file = './scatterplot/index.html',
                    verbose = True)

    (options, args) = parser.parse_args()

    object_to_scatterplot(options.obj_file, options.scatter_file)
