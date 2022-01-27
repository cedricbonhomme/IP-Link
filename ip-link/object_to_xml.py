#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_xml

Loads a serialized graph object in memory and generates an XML file.

Example of an XML file:

<?xml version="1.0" ?>
<IP-Link>
    <ip_packet source_ip="202.30.242.24">
        <ip_packet destination_ip="192.168.1.2" weight="1"/>
    </ip_packet>
    <ip_packet source_ip="192.168.1.2">
        <ip_packet destination_ip="202.30.242.24" weight="1"/>
        <ip_packet destination_ip="200.151.67.119" weight="1"/>
        <ip_packet destination_ip="194.154.192.1" weight="1"/>
        <ip_packet destination_ip="207.46.134.155" weight="4"/>
    </ip_packet>
    <ip_packet source_ip="194.154.192.1">
        <ip_packet destination_ip="192.168.1.2" weight="1"/>
    </ip_packet>
    <ip_packet source_ip="200.151.67.119">
        <ip_packet destination_ip="192.168.1.2" weight="1"/>
    </ip_packet>
</IP-Link>
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2009/02/20 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import pickle
from xml.dom.minidom import Document


def object_to_xml(obj_file, xml_file):
    """Gnerate an XML file."""
    dic_obj = open(obj_file, "rb")
    if options.verbose:
        print("Loading dictionary...")
    dic_ip = pickle.load(dic_obj)

    if options.verbose:
        print("Creating XML file...")
    doc = Document()
    racine = doc.createElement("IP-Link")
    doc.appendChild(racine)

    for ip_src in dic_ip:
        ipsrc = doc.createElement("ip_packet")
        ipsrc.setAttribute("source_ip", ip_src)
        racine.appendChild(ipsrc)
        for ip_dst in dic_ip[ip_src]:
            ipdst = doc.createElement("ip_packet")
            ipdst.setAttribute("destination_ip", ip_dst)
            ipdst.setAttribute("weight", str(dic_ip[ip_src][ip_dst]))
            ipsrc.appendChild(ipdst)

    # Elegant display of the XML object
    # print doc.toprettyxml()

    try:
        file = open(xml_file, "w")
        file.write("%s" % doc.toxml().encode("utf-8"))
    except IOError as e:
        print("Writting error :", e)
    finally:
        file.close()


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="xml_file", help="XML file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", xml_file="./data/ip.xml", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_xml(options.obj_file, options.xml_file)
