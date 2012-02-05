#! /usr/local/bin/python
#-*- coding: utf-8 -*-

"""pcap_to_object

Generate a serialized graph object from a pcap file.

Extract from a cap file from the "any" interface .
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/02/19 $"
__copyright__ = "Copyright (c) 2009-2012 Jerome Hussenet, Copyright (c) 2009-2012 Cedric Bonhomme"
__license__ = "Python"

import os
import sys

import pickle

import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets


def pcap_to_object(pcap_file, obj_file):
    """Create a Python serialized graph object.
    
    Read the pcap file given in parameter, extracts source and destination IP
    and write a serialized graph object.
    """
    reader = pcapy.open_offline(pcap_file)
    print reader.datalink()
    print pcapy.DLT_LINUX_SLL
    eth_decoder = Decoders.EthDecoder()
    sll_decoder = Decoders.LinuxSLLDecoder()
    ip_decoder = Decoders.IPDecoder()

    dic_ip = {}

    tts_min = 1000
    tts_max = 2000

    if options.verbose:
        print "Reading pcap file..."
    while True:
        try:
            (header, payload) = reader.next()
            if True: #tts_min <= header.getts()[0] <= tts_max:
                #ethernet = eth_decoder.decode(payload)
                sll = sll_decoder.decode(payload)
                if sll.get_ether_type() == Packets.IP.ethertype:
                    #ip = ip_decoder.decode(payload[ethernet.get_header_size():])
                    ip_src = sll.child().get_ip_src()
                    ip_dst = sll.child().get_ip_dst()
                    print ip_src, ip_dst
                    if ip_src not in dic_ip:
                        dic_ip[ip_src] = {}
                        dic_ip[ip_src][ip_dst] = 1
                    else:
                        if ip_dst not in dic_ip[ip_src]:
                            dic_ip[ip_src][ip_dst] = 1
                        else:
                            dic_ip[ip_src][ip_dst] += 1
        except Packets.ImpactPacketException, e:
            print e
        except:
            break

    if options.verbose:
        print "Serialization..."
    dic_obj = open(obj_file, "w")
    pickle.dump(dic_ip, dic_obj)
    dic_obj.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="pcap_file",
                    help="pcap file")
    parser.add_option("-o", "--output", dest="obj_file",
                    help="Python serialized object")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose",
                    help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(pcap_file = './captures/jubrowska-capture_1.cap',
                    obj_file = './data/dic.pyobj',
                    verbose = True)

    (options, args) = parser.parse_args()

    pcap_to_object(options.pcap_file, options.obj_file)
