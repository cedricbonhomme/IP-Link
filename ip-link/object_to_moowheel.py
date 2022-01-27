#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_moowheel.py

Visualize data using Javascript and the <canvas> object.

http://code.google.com/p/moowheel/
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/03/26 $"
__copyright__ = "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import pickle


def object_to_moowheel(obj_file, moo_file):
    """Generate MooWheel file."""
    dic_obj = open(obj_file, "r")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("Creating MooWheel file...")

    wheel_data = '<html>\n\t<head>\n\t<title>IP-Link - MooWheel</title>\n\n' + \
        '\t<style type="text/css" media="screen">\n' + \
        '\thtml, body { padding: 0; margin: 0;}\n' + \
        '\tbody {text-align: left; background-color: #000;\n' + \
        '\tpadding: 10px 0 0 10px;}\n' + \
        '\tdiv#canvas {display: block; border: 1px solid #fff;\n' + \
        '\tbackground-color: #000;\n' + \
        '\tfont: 12px Verdana, Tahoma, Arial, sans-serif;' + \
        '\tcolor: #fff;}\n\t</style>\n\n' + \
        '\t<script type="text/javascript" src="./excanvas.js"></script>\n' + \
        '\t<script type="text/javascript" src="./canvastext.js"></script>\n' + \
        '\t<script type="text/javascript" src="./mootools-1.2-core-nc.js"></script>\n' + \
        '\t<script type="text/javascript" src="./mootools-1.2-more.js"></script>\n' + \
        '\t<script type="text/javascript" src="./moowheel.js"></script>\n\n' + \
        '\t<script type="text/javascript">\n' + \
        '\twindow.onload = function() {\n' + \
        '\tvar wheelData = '

    wheel_data += '['
    for ip_src in dic_ip:
        wheel_data += '\t{"id":"' + ip_src + '", "text":" ' + ip_src + '"'
        wheel_data += ', "connections":['

        for ip_dst in dic_ip[ip_src]:
            wheel_data += '"' + ip_dst + '",\n\t\t'

        wheel_data = wheel_data[:-4]
        wheel_data += ']},\n'

    # dst problem
    dst_fix = []
    for ip_src in dic_ip:
        for ip_dst in dic_ip[ip_src]:
            if ip_dst not in dic_ip and ip_dst not in dst_fix:
                wheel_data += '\t{"id":"' + ip_dst + \
                    '", "text":" ' + ip_dst + '", "connections":[]},\n'
                dst_fix.append(ip_dst)
    # dst problem
    wheel_data = wheel_data[:-2] + ']'

    wheel_data += "\n\n\tvar wheel = new MooWheel(wheelData, $('canvas'));" + \
        '};\n\t</script>\n\t</head>\n\t<body>\n\t\t<div id="canvas"></div>\n\t</body>\n</html>'

    if options.verbose:
        print("Writting file.")
    mw = open(moo_file, "w")
    mw.write(wheel_data)
    mw.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file",
                      help="Python serialized object")
    parser.add_option("-o", "--output", dest="moo_file",
                      help="MooWheel HTML file")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(obj_file='./data/dic.pyobj',
                        moo_file='./moowheel/moowheel.html',
                        verbose=True)

    (options, args) = parser.parse_args()

    object_to_moowheel(options.obj_file, options.moo_file)
    object_to_moowheel(options.obj_file, options.moo_file)
