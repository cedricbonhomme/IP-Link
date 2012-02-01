#! /bin/sh




mkdir captures data
sudo tcpdump -p -i eth0 -s 0 -w captures/snif.pcap
python pcap_to_object1.py -i captures/snif.pcap -o data/dic.pyobj
python object_to_graphviz.py -i ./data/dic.pyobj
dot -Tpng -o ./data/graphviz.png ./data/ip.dot
