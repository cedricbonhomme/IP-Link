#! /usr/local/bin/python
#-*- coding: utf-8 -*-

"""pcap_to_sqlite

Generate the SQLite base from the pcap file.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/02/19 $"
__copyright__ = "Copyright (c) 2009 Jerome Hussenet, Copyright (c) 2009 Cedric Bonhomme"
__license__ = "Python"

import os
import sys

import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

import sqlite3


def pcap_to_sqlite(pcap_file, sqlite_file):
    """Generate the SQLite base.
    
    Read the pcap file given in parameter, extracts source and destination IP
    and create the SQLite base.
    """
    reader = pcapy.open_offline(pcap_file)
    eth_decoder = Decoders.EthDecoder()
    ip_decoder = Decoders.IPDecoder()

    if options.verbose:
        print "Reading pcap file..."
    liste = []
    while True:
        try:
            (header, payload) = reader.next()
            ethernet = eth_decoder.decode(payload)
            if ethernet.get_ether_type() == Packets.IP.ethertype:
                ip = ip_decoder.decode(payload[ethernet.get_header_size():])
                liste.append((str(header.getts()), ip.get_ip_src(), ip.get_ip_dst()))
        except:
            break

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    if options.verbose:
        print "Creating table."
    c.execute('''create table ip_link
    (tts real, ip_src text, ip_dst text)''')

    if options.verbose:
        print "Inserting values in the table..."
    for t in liste:
        c.execute('insert into ip_link values (?,?,?)', t)

    conn.commit()
    c.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="pcap_file",
                    help="pcap file")
    parser.add_option("-o", "--output", dest="sqlite_file",
                    help="SQLite base")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose",
                    help="be vewwy quiet (I'm hunting wabbits)")
    parser.set_defaults(pcap_file = './captures/jubrowska-capture_1.cap',
                    sqlite_file = './data/ip.sql',
                    verbose = True)

    (options, args) = parser.parse_args()

    pcap_to_sqlite(options.pcap_file, options.sqlite_file)
