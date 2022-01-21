#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""pcap_to_sqlite

Generate the SQLite base from the pcap file.

Data extracted from the capture are :
 - the timestamp ;
 - destination address ;
 - source address ;
 - destination port ;
 - source port ;
 - protocol (TCP/UDP).

http://sourceforge.net/projects/pylibpcap/
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2012/02/05 $"
__copyright__ = (
    "Copyright (c) 2010-2012 Jerome Hussenet, Copyright (c) 2010-2012 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import os
import sys
import pcap
import socket
import struct

import sqlite3


def decode_tcp_segment(s):
    """
    Return the source and destination ports of a TCP segment.
    """
    d = {}
    d["source_port"] = socket.ntohs(struct.unpack("H", s[0:2])[0])
    d["destination_port"] = socket.ntohs(struct.unpack("H", s[2:4])[0])
    return d


def decode_udp_segment(s):
    """
    Return the source and destination ports of a UDP segment.
    """
    d = {}
    d["source_port"] = socket.ntohs(struct.unpack("H", s[0:2])[0])
    d["destination_port"] = socket.ntohs(struct.unpack("H", s[2:4])[0])
    return d


def decode_ip_packet(s):
    """
    Decode IP packets.
    """
    d = {}
    # d['version'] = (ord(s[0]) & 0xf0) >> 4
    d["header_len"] = ord(s[0]) & 0x0F
    # d['tos'] = ord(s[1])
    # d['total_len'] = socket.ntohs(struct.unpack('H',s[2:4])[0])
    # d['id'] = socket.ntohs(struct.unpack('H',s[4:6])[0])
    # d['flags'] = (ord(s[6]) & 0xe0) >> 5
    # d['fragment_offset'] = socket.ntohs(struct.unpack('H',s[6:8])[0] & 0x1f)
    # d['ttl'] = ord(s[8])
    d["protocol"] = ord(s[9])
    # d['checksum'] = socket.ntohs(struct.unpack('H',s[10:12])[0])
    d["source_address"] = pcap.ntoa(struct.unpack("i", s[12:16])[0])
    d["destination_address"] = pcap.ntoa(struct.unpack("i", s[16:20])[0])
    # if d['header_len'] > 5:
    # d['options'] = s[20:4*(d['header_len']-5)]
    # else:
    # d['options'] = None
    d["data"] = s[4 * d["header_len"] :]
    return d


def pcap_to_sqlite(pcap_file, sqlite_file):
    """Generate the SQLite base.

    Read the pcap file given in parameter, extracts source and destination IP
    and create the SQLite base.
    """
    reader = pcap.pcapObject()
    reader.open_offline(pcap_file)

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    if options.verbose:
        print("Creating table.")
    c.execute(
        """create table ip_link
    (tts real, ip_src text, ip_dst text, prot int1, port_src int4, port_dst int4)"""
    )

    if options.verbose:
        print("Reading pcap and inserting values in the table...")
    stat = {}
    while True:
        try:
            (_, payload, tts) = next(reader)
        except:
            break
        if payload[12:14] == "\x08\x00":
            decoded_ip_packet = decode_ip_packet(payload[14:])
            if decoded_ip_packet["protocol"] == 17:
                decoded_segment = decode_tcp_segment(decoded_ip_packet["data"])
            elif decoded_ip_packet["protocol"] == 6:
                decoded_segment = decode_udp_segment(decoded_ip_packet["data"])
            else:
                decoded_segment = None
            stat[decoded_ip_packet["protocol"]] = (
                stat.get(decoded_ip_packet["protocol"], 0) + 1
            )
            if decoded_segment != None:
                c.execute(
                    "insert into ip_link values (?,?,?,?,?,?)",
                    (
                        str(tts),
                        decoded_ip_packet["source_address"],
                        decoded_ip_packet["destination_address"],
                        decoded_ip_packet["protocol"],
                        decoded_segment["source_port"],
                        decoded_segment["destination_port"],
                    ),
                )

    conn.commit()
    c.close()
    if options.verbose:
        print(stat)


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="pcap_file", help="pcap file")
    parser.add_option(
        "-o", "--output", dest="sqlite_file", help="SQLite base to generate"
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
        sqlite_file="./data/ip.sql",
        verbose=True,
    )

    (options, args) = parser.parse_args()

    pcap_to_sqlite(options.pcap_file, options.sqlite_file)
