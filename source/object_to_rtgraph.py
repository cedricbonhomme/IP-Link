#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_rtgraph

Load a serialized object in memory and generate 3D dynamic graph.
This module uses RealTime 3D Graph.

It is necessary to have the modules :
 - python-visual ;
 - povexport ;
 - PyInline for better performance.

PyInline and povexport are already included with IP-Link.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/03/05 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import os
import sys
import time
import threading

import pickle

from rtgraph3d.rtg_cli import *
from rtgraph3d.rtgraph3d import *


def object_to_rtgraph(obj_file):
    """Generates a 3D dynamic graphics."""
    dic_obj = open(obj_file, "r")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("Creation of the command for RealTime 3D Graph...")
    command = ""
    edges = []
    for ip_src in dic_ip:
        for ip_dst in dic_ip[ip_src]:
            if (ip_src, ip_dst) not in edges:
                edges.extend([(ip_src, ip_dst), (ip_dst, ip_src)])
                command += "edge " + ip_src + " " + ip_dst + "\n"
    command += "quit"

    if options.verbose:
        print("Launching the RTgraph3D window thread")
    a = threading.Thread(None, rtggraph_launch, None)
    a.start()

    time.sleep(1)

    cmd = 'echo "' + command + '" | python ./rtgraph3d/rtg_cli.py'
    if options.verbose:
        print("command to execute :")
        print(cmd)

    (child_stdin, child_stdout, child_stderr) = os.popen3(cmd)
    stderr = child_stderr.readlines()
    stdout = child_stdout.readlines()
    child_stdin.close()
    child_stdout.close()
    child_stderr.close()

    if options.verbose:
        print("Problem(s) :")
        print(stderr)
        print("\nOutput :")
        print(stdout)


def rtggraph_launch():
    INPUT = [sys.stdin]
    STARTFILE = None
    SAVEFILE = None
    STEREO = None
    CINEMATIC = Cinematic.dynamic
    POVDUMP = None
    MODE = 0
    try:
        opts = getopt.getopt(sys.argv[1:], "htr:w:s:c:P:m:q:i")

        for opt, optarg in opts[0]:
            if opt == "-h":
                usage()
            elif opt == "-t":
                MODE = socket.SOCK_STREAM
            elif opt == "-r":
                STARTFILE = optarg
            elif opt == "-s":
                STEREO = optarg
            elif opt == "-w":
                SAVEFILE = optarg
            elif opt == "-m":
                try:
                    MODE = {"p": 1, "c": 2, "s": 3}[optarg.lower()]
                except KeyError:
                    raise getopt.GetoptError("unkonwn mode [%s]" % optarg)
            elif opt == "-P":
                POVDUMP = optarg
            elif opt == "-c":
                if optarg.startswith("s"):  # static
                    CINEMATIC = Cinematic.static
                elif optarg.startswith("d"):  # dynamic
                    CINEMATIC = Cinematic.dynamic
    except getopt.GetoptError as msg:
        log.exception(msg)
        sys.exit(-1)

    gobject.threads_init()
    dbus.glib.init_threads()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    name = dbus.service.BusName("org.secdev.rtgraph3d", bus)
    svc = RTGraphService(
        bus,
        "/control",
        get_physics_engine(MODE),
        INPUT,
        startfile=STARTFILE,
        savefile=SAVEFILE,
        stereo=STEREO,
    )

    if CINEMATIC == Cinematic.dynamic:
        thread.start_new_thread(
            cinematic_thread,
            (
                svc,
                POVDUMP,
            ),
        )

    mainloop = gobject.MainLoop()
    log.info("Entering main loop")
    mainloop.run()


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

    object_to_rtgraph(options.obj_file)
