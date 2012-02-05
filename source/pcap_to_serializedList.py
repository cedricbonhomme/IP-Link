#! /usr/bin/env python
#-*- coding: utf-8 -*-


"""pcap_to_serializedList.py

Generate a serialized list object from the pcap file.

This script uses Pylibpcap which is faster than pcapy.

The object list generated contains the same information as the basis sqlite.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/02/20 $"
__copyright__ = "Copyright (c) 2009-2012 Jerome Hussenet, Copyright (c) 2009-2012 Cedric Bonhomme"
__license__ = "Python"

import pcap

import socket
import struct

import pickle


def decode_ip_packet(s):
    """Decode IP packets"""
    d = {}
    #d['version'] =(ord(s[0]) & 0xf0) >> 4
    #d['header_len'] = ord(s[0]) & 0x0f
    #d['tos'] = ord(s[1])
    #d['total_len'] = socket.ntohs(struct.unpack('H', s[2:4])[0])
    #d['id'] = socket.ntohs(struct.unpack('H', s[4:6])[0])
    #d['flags'] = (ord(s[6]) & 0xe0) >> 5
    #d['fragment_offset'] = socket.ntohs(struct.unpack('H', s[6:8])[0] & 0x1f)
    #d['ttl'] = ord(s[8])
    #d['protocol'] = ord(s[9])
    #d['checksum'] = socket.ntohs(struct.unpack('H', s[10:12])[0])
    d['source_address'] = pcap.ntoa(struct.unpack('i', s[12:16])[0])
    d['destination_address'] = pcap.ntoa(struct.unpack('i', s[16:20])[0])
    #if d['header_len'] > 5:
      #d['options'] = s[20:4*(d['header_len']-5)]
    #else:
      #d['options'] = None
    #d['data'] = s[4 * d['header_len']:]
    return d

def pcap_to_serializedList(pcap_file, obj_file):
    reader = pcap.pcapObject()
    reader.open_offline(pcap_file)

    liste_ip = []

    if options.verbose:
        print "Reading pcap file..."
    while True:
        try:
            (_, payload, tts) = reader.next()
        except:
            break
        if payload[12:14] == '\x08\x00':
            decoded_ip_packet = decode_ip_packet(payload[14:])
            liste_ip.append((tts, decoded_ip_packet['source_address'], \
                            decoded_ip_packet['destination_address']))

    if options.verbose:
        print "Serialization..."
    liste_obj = open(obj_file, "w")
    pickle.dump(liste_ip, liste_obj)
    liste_obj.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="pcap_file",
                    help="pcap file")
    parser.add_option("-o", "--output", dest="objlist_file",
                    help="Python serialized object")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose",
                    help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(pcap_file = './captures/jubrowska-capture_1.cap',
                    objlist_file = './data/list.pyobj',
                    verbose = True)

    (options, args) = parser.parse_args()

    pcap_to_serializedList(options.pcap_file, options.objlist_file)
