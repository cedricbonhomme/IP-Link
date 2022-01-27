#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_html.py

Generate an HTML gallery.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2009/02/23 $"
__copyright__ = (
    "Copyright (c) 2009-2013 Jerome Hussenet, Copyright (c) 2009-2022 Cédric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

import os
import sys
import pickle

import matplotlib.pyplot as plt
import numpy as np


def usage():
    """Display help."""
    print("Usage :\n\tpython " + sys.argv[0] + " obj_file")
    print("\tpython " + sys.argv[0] + " --help\n")
    print("Example:\n\t" + "python " + sys.argv[0] + " dic.pyobj\n")
    print(__author__)
    print(__version__, __date__)
    print(__copyright__)
    print("License " + __license__)
    exit(1)


if len(sys.argv) == 2:
    if sys.argv[1][2:] == "help":
        usage()
    try:
        obj_file = str(sys.argv[1])
    except Exception:
        usage()
    if not os.path.isfile(obj_file):
        print(" does not exist.")
        exit(1)
elif len(sys.argv) == 1:
    obj_file = "./data/dic.pyobj"
    print("Default arguments :")
    print("\tPython object file :", obj_file)
else:
    usage()


dic_obj = open(obj_file, "r")
print("Loading dictionary...")
dic_ip = pickle.load(dic_obj)


def create_bar_chart(ip_src, liste_ip_dst, file_name):
    """Creates a histogram.

    Most contacted IP by 'ip_src'.
    A maximum of ten IP are displayed.
    """
    fig, ax = plt.subplots()

    length = len(liste_ip_dst)
    ind = np.arange(length)  # ip destinations in abscissa
    width = 0.35  # bars width

    ip_dst = [elem[0] for elem in liste_ip_dst]
    weight = [int(elem[1]) for elem in liste_ip_dst]

    max_weight = max(weight)  # maximal weight

    p = ax.bar(ind, weight, width, color="r")

    ax.set_ylabel("Weight")
    ax.title("Histogram")
    ax.set_xticks(ind + (width / 2), list(range(1, len(ip_dst) + 1)))
    ax.set_xlim(-width, len(ind))

    # changing the ordinate scale according to the max.
    if max_weight <= 100:
        ax.set_ylim(0, max_weight + 5)
        ax.set_yticks(ax.arange(0, max_weight + 5, 5))
    elif max_weight <= 200:
        ax.set_ylim(0, max_weight + 10)
        ax.set_yticks(ax.arange(0, max_weight + 10, 10))
    elif max_weight <= 600:
        ax.set_ylim(0, max_weight + 25)
        ax.set_yticks(ax.arange(0, max_weight + 25, 25))
    elif max_weight <= 800:
        ax.set_ylim(0, max_weight + 50)
        ax.set_yticks(ax.arange(0, max_weight + 50, 50))

    ax.legend()

    ax.savefig(file_name, dpi=150)
    ax.close()


# def create_pie_chart(ip_src, liste_ip_dst, file_name):
#     """Creates a circular graph.
#
#     Return the list of the most contacted IP by 'ip_src'.
#     A maximum of ten IP are displayed.
#     """
#     np.figure(1, figsize=(6, 6))
#     ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
#
#     labels = tuple([elem[0] for elem in liste_ip_dst])
#     fracs = [int(elem[1]) for elem in liste_ip_dst]
#
#     # explode=(0, 0.06, 0, 0, 0) # bring some relief on the parts
#     explode = (0,) * len(fracs)  # no relief
#     pylab.pie(
#         fracs,
#         explode=explode,
#         labels=list(range(1, len(labels) + 1)),
#         autopct="%1.1f%%",
#         shadow=True,
#     )
#     pylab.title(("Circular graph"))
#
#     pylab.savefig(file_name, dpi=180)
#     pylab.close()


# Creating images directory
try:
    os.makedirs("./html" + os.sep + "images")
except Exception as e:
    print("Writting error :", e)


"""Generates HTML gallery.

Go through all the sources and destinations IP
in order to create the details pages.
"""
html_head = (
    "<html>\n<head>\n<title>IP-Link</title>\n</head>\n<body><h1>IP-Link Report</h1>"
)
pied = (
    "<h6>IP-Link - Copyright (c) 2009-2013 J&eacute;r&ocirc;me Hussenet, "
    + "Copyright (c) 2009-2013 C&eacute;dric Bonhomme</h6></body>\n</html>"
)
html = html_head + "\n"


# Main page
print("Creating HTML index...")
for ip_src in dic_ip:

    # Table of the main page
    html += (
        "<h2>IP contacted by "
        + '<a href="./'
        + ip_src
        + '.details.html">'
        + ip_src
        + "</a></h2>\n\n"
    )
    html += '<div align="center">\n<table border="1" width="50% align="center">\n'
    for ip_dst in dic_ip[ip_src]:
        html += (
            "<tr>\n<td>"
            + ip_dst
            + "</td>"
            + '<td align="center">'
            + str(dic_ip[ip_src][ip_dst])
            + "</td>\n</tr>\n"
        )
    html += "</table>\n</div>\n\n"

    # Details HTMl pages
    html_details = (
        html_head
        + "\n\n<h2>Report for "
        + ip_src
        + "</h2><br />\n\n"
        + "<h3>Most contacted IP by "
        + ip_src
        + "</h3><br />\n\n"
    )
    html_details += (
        '<div align="center">\n<img src="./images/'
        + ip_src.replace(".", "")
        + '_hist.png" align="bottom" alt="'
        + ip_src
        + '" title="'
        + ip_src
        + '" />\n</div>'
    )
    html_details += "\n\n<br /><br />\n"
    html_details += (
        '<div align="center">\n<img src="./images/'
        + ip_src.replace(".", "")
        + '_pie.png" align="bottom" alt="'
        + ip_src
        + '" title="'
        + ip_src
        + '" />\n</div>'
    )
    html_details += "\n\n<h3>Legend :</h3>\n<ul>\n"

    # List of tuples (ip_dest, weight) in relation with ip_src
    liste = [(elem, dic_ip[ip_src][elem]) for elem in dic_ip[ip_src]]
    # sorting and selection of ten most viewed IP
    liste = sorted(liste, key=lambda x: (x[1], x[0]), reverse=True)[:10]
    ipdst = [elem[0] for elem in liste]  # IP
    weight = [elem[1] for elem in liste]  # IP associated weight

    # graphs legend:
    for i, ip in enumerate(ipdst):
        if ip in dic_ip:
            html_details += (
                "<li>"
                + str(i + 1)
                + " : "
                + '<a href="./'
                + ip
                + '.details.html">'
                + ip
                + "</a>"
                + ", weight : "
                + str(weight[i])
                + "</li>\n"
            )
        else:
            html_details += (
                "<li>"
                + str(i + 1)
                + " : "
                + ip
                + ", weight : "
                + str(weight[i])
                + "</li>\n"
            )
    html_details += "</ul>\n"
    html_details += pied

    # Creation of the histogram
    print(
        "Creation of the histogram : ./html/images/"
        + ip_src.replace(".", "")
        + "_hist.png"
    )
    create_bar_chart(
        ip_src, liste, "./html/images/" + ip_src.replace(".", "") + "_hist.png"
    )
    # Creation of the circular graph
    print(
        "Creation of the circular graph : ./html/images/"
        + ip_src.replace(".", "")
        + "_pie.png"
    )
    # create_pie_chart(ip_src, liste ,"./html/images/" + ip_src.replace('.', '') + "_pie.png")

    # Writting details pages
    print("Creating the HTML page for", ip_src)
    try:
        html_file = open("./html/" + ip_src + ".details.html", "w")
        html_file.write("%s" % html_details)
    except IOError as e:
        print("Writting error :", e)
    finally:
        html_file.close()

# Writting the main page
html += pied
try:
    html_file = open("./html/index.html", "w")
    html_file.write("%s" % html.encode("utf-8"))
except IOError as e:
    print("Writting error :", e)
    pass
finally:
    html_file.close()
