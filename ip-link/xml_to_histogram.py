#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""xml_to_histogram.py

Uses pylab Python module to display a histogram wich represent
the IP contacted by a source IP.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/02/22 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"


def xml_to_histogram(xml_file, ip_src):
    """Display a histogram.

    The generated histogram corresponds to the 10 most IP visited by 'ip_src".
    """
    # list of IP contacted by ip_src.
    from xml.dom.minidom import parse

    try:
        doc = parse("./data/ip.xml")
    except Exception:
        return
    # contains the tuples (ip_dest, weight)
    liste = []
    try:
        for ipsrc in doc.getElementsByTagName("IP-Link").item(0).childNodes:
            if ipsrc.getAttribute("source_ip") == ip_src:
                for ip_dst in ipsrc.getElementsByTagName("ip_packet"):
                    liste.append(
                        (
                            ip_dst.getAttribute("destination_ip"),
                            ip_dst.getAttribute("weight"),
                        )
                    )
    except Exception:
        pass

    if liste:
        liste = sorted(liste, key=lambda x: (x[1], x[0]), reverse=True)[:10]

        length = len(liste)
        ind = pylab.arange(length)  # ip destinations in abscissa
        width = 0.35  # bars width

        ip_dst = [elem[0] for elem in liste]
        weight = [int(elem[1]) for elem in liste]

        max_weight = max(weight)  # max weight

        p = pylab.bar(ind, weight, width, color="r")

        pylab.ylabel("weight")
        pylab.title("IPs contacted by " + ip_src)
        pylab.xticks(ind + (width / 2), list(range(1, len(ip_dst) + 1)))
        pylab.xlim(-width, len(ind))

        # changing the ordinate scale according to the max.
        if max_weight <= 100:
            pylab.ylim(0, max_weight + 5)
            pylab.yticks(pylab.arange(0, max_weight + 5, 5))
        elif max_weight <= 200:
            pylab.ylim(0, max_weight + 10)
            pylab.yticks(pylab.arange(0, max_weight + 10, 10))
        elif max_weight <= 600:
            pylab.ylim(0, max_weight + 25)
            pylab.yticks(pylab.arange(0, max_weight + 25, 25))
        elif max_weight <= 800:
            pylab.ylim(0, max_weight + 50)
            pylab.yticks(pylab.arange(0, max_weight + 50, 50))

        pylab.show()
    else:
        print("No result for", ip_src)


if __name__ == "__main__":
    # Point of entry in execution mode.
    try:
        import pylab
    except ImportError:
        print("Error : pylab module missing.")
        print("http://matplotlib.sourceforge.net/")
        exit(1)

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="xml_file", help="XML file")
    parser.add_option("-s", "--source-ip", dest="ip_src", help="Source IP")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(xml_file="./data/ip.csv", ip_src="192.168.1.1", verbose=True)

    (options, args) = parser.parse_args()

    xml_to_histogram(options.xml_file, options.ip_src)
