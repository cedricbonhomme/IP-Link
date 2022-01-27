#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""pcap_to_object

Generate a serialized graph object from the pcap file.
"""

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.5 $"
__date__ = "$Date: 2009/02/20 $"
__revision__ = "$Date: 2022/01/27 $"
__copyright__ = "Copyright (c) 2009-2022 Cedric Bonhomme"
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import pickle

from pypacker import ppcap
from pypacker.layer12 import ethernet
from pypacker.layer3 import ip

from collections import defaultdict
from collections import Counter


def ip_dict():
    return defaultdict(Counter)


def pcap_to_object(pcap_file, obj_file):
    """Create a Python serialized graph object.

    Read the pcap file given in parameter, extracts source and destination IP
    and write a serialized graph object.
    """
    dic_ip = ip_dict()
    reader = ppcap.Reader(filename=pcap_file)

    if options.verbose:
        print("Reading pcap file...")
    for ts, buf in reader:
        eth = ethernet.Ethernet(buf)

        if eth[ip.IP] is not None:
            # print("%d: %s:%s -> %s:%s" % (ts, eth[ip.IP].src_s,
            #                             eth[tcp.TCP].sport, eth[ip.IP].dst_s,
            #                             eth[tcp.TCP].dport))
            dic_ip[eth[ip.IP].src_s][eth[ip.IP].dst_s] += 1

    if options.verbose:
        print("Serialization...")
    dic_obj = open(obj_file, "wb")
    pickle.dump(dic_ip, dic_obj)
    dic_obj.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="pcap_file", help="pcap file")
    parser.add_option(
        "-o", "--output", dest="obj_file", help="Python serialized object"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        pcap_file="./captures/jubrowska-capture_1.cap",
        obj_file="./data/dic.pyobj",
        verbose=True,
    )

    (options, args) = parser.parse_args()

    pcap_to_object(options.pcap_file, options.obj_file)
