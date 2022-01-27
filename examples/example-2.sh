#! /bin/sh


mkdir captures data
sudo tcpdump -p -i eth0 -s 0 -w captures/snif.pcap
ip-link/pcap_to_object.py -i captures/snif.pcap -o data/dic.pyobj
ip-link/object_to_rtgraph.py
