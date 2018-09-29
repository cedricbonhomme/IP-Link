Extraction
==========

pcap_to_sqlite.py
-----------------

Generate the SQLite base.

Read the pcap file given in parameter, extracts source and destination IP and create the SQLite base.

Options:

- -i, —input pcap file, (provided by tcpdump for example)
- -o, —output sqlite file
- -q, —quiet disable print on stdout


pcap_to_sqlite.sh
-----------------

Generate the SQLite base.

This script uses tcpdump and sqlite3.

Parameters:

- pcap file


pcap_to_object.py
-----------------

Generate a serialized graph object.

Read the pcap file given in parameter, extracts source and destination IP and create the graph onject.

Options:

- -i, —input pcap file
- -o, —output python serialized object
- -q, —quiet disable print on stdout



Visualization
=============

object_to_circos.py
-------------------

Generate an input file (matrix) for Circos.

Loads a serialized graph object in memory and create the matrix for Circos.

Options:

- -i, —input Python serialized object
- -o, —output Circos input file
- -q, —quiet disable print on stdout

object_to_moowheel.py
---------------------

Generate an HTML file using Javascript and the <canvas> object.

Loads a serialized graph object in memory and create the MooWheel connections graph.

Options:

- -i, —input Python serialized object
- -o, —output MooWheel HTML file
- -q, —quiet disable print on stdout
