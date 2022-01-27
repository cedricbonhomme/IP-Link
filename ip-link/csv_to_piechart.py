#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""csv_to_piechart.py

Uses pylab Python module to display a pie chart wich represent
the IP contacted by a source IP.
"""

import csv


class excel_french(csv.Dialect):
    delimiter = ";"
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL


csv.register_dialect("excel_french", excel_french)


def csv_to_piechart(csv_file, ip_src):
    """Display the pie chart.

    The generated histogram corresponds to the 10 most IP visited by 'ip_src'.
    """
    # list of IP contacted by ip_src.
    cr = csv.reader(open(csv_file, "rb"), "excel_french")
    # contains the tuples (ip_dest, weight)
    liste = []
    for row in cr:
        if row[0] == ip_src:
            liste.append((row[1], row[2]))

    if liste:
        liste = sorted(liste, key=lambda x: (x[1], x[0]), reverse=True)[:10]

        pylab.figure(1, figsize=(6, 6))
        ax = pylab.axes([0.1, 0.1, 0.8, 0.8])

        labels = tuple([elem[0] for elem in liste])
        fracs = [int(elem[1]) for elem in liste]

        # explode=(0, 0.06, 0, 0, 0) # parts relief
        explode = (0,) * len(fracs)  # no relief
        pylab.pie(fracs, explode=explode, labels=labels, autopct="%1.0f%%", shadow=True)
        pylab.title(("IPs contacted by " + ip_src))

        pylab.show()
    else:
        print("No result for ", ip_src)


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
    parser.add_option("-i", "--input", dest="csv_file", help="CSV file")
    parser.add_option("-s", "--source-ip", dest="ip_src", help="Source IP")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(csv_file="./data/ip.csv", ip_src="192.168.1.1", verbose=True)

    (options, args) = parser.parse_args()

    csv_to_piechart(options.csv_file, options.ip_src)
