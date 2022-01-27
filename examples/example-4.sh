#!/bin/bash

#
# assumptions:
#   - there is an lo device with 127.0.0.1/8
#   - commands are run from the ip-link/source directory
#   - commands tested on a up to date Fedora 20 host
#

# drop all traffic to 127.0.0.3 in order to create a one-way flow
sudo iptables -I INPUT -d 127.0.0.3 -j DROP

# dump lo
sudo tcpdump -i lo -w out.pcap &

# pinging 127.0.0.2 from 127.0.0.1 will succeed
ping -c 3 127.0.0.2

# pinging will fail
ping -c 3 127.0.0.3

# pinging 127.0.0.4 from 127.0.0.1 will succeed
ping -c 3 127.0.0.4

# pinging 127.0.0.5 from 127.0.0.1 will succeed
ping -c 3 127.0.0.5

# pinging 127.0.0.5 from 127.0.0.10 will succeed
ping -c 3 -I 127.0.0.10 127.0.0.5

# pinging 127.0.0.3 from multiple addresses will fail
# uncomment next command to create multiple one-way flows
#for I in {1..9}; do ping -c 3 -I 127.0.0.1$I 127.0.0.3; done

sudo pkill tcpdump

ip-link/pcap_to_object.py -i out.pcap -o out.pyobj

ip-link/object_to_moowheel.py -i out.pyobj
