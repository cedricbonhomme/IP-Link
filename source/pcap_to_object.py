#! /usr/bin/env python
#-*- coding: utf-8 -*-


"""pcap_to_object

Generate a serialized graph object from the pcap file.

This script uses Pylibpcap which is faster than pcapy.

http://sourceforge.net/projects/pylibpcap/
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/02/20 $"
__copyright__ = "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2013 Cedric Bonhomme"
__license__ = "Python"

import os
import sys

import pcap
import socket
import struct

import pickle


def decode_ip_packet(s):
    """Decode IP packets"""
    d = {}
    #d['version'] = (ord(s[0]) & 0xf0) >> 4
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
    #d['data'] = s[4*d['header_len']:]
    return d

def pcap_to_object(pcap_file, obj_file):
    """Create a Python serialized graph object.
    
    Read the pcap file given in parameter, extracts source and destination IP
    and write a serialized graph object.
    """
    reader = pcap.pcapObject()
    reader.open_offline(pcap_file)

    if options.verbose:
        print "Reading pcap file..."
    dic_ip = {}
    while True:
        try:
            (_, payload, tts) = reader.next()
        except:
            break
        if payload[12:14] == '\x08\x00':
            decoded_ip_packet = decode_ip_packet(payload[14:])
            if decoded_ip_packet['source_address'] not in dic_ip:
                dic_ip[decoded_ip_packet['source_address']] = {}
                dic_ip[decoded_ip_packet['source_address']] \
                        [decoded_ip_packet['destination_address']] = 1
            else:
                if decoded_ip_packet['destination_address'] not in \
                                        dic_ip[decoded_ip_packet['source_address']]:
                    dic_ip[decoded_ip_packet['source_address']] \
                        [decoded_ip_packet['destination_address']] = 1
                else:
                    dic_ip[decoded_ip_packet['source_address']] \
                        [decoded_ip_packet['destination_address']] += 1

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
