# IP-Link

[![builds.sr.ht status](https://builds.sr.ht/~cedric/ip-link.svg)](https://builds.sr.ht/~cedric/ip-link)


## Presentation

The goal of [IP-Link](https://git.sr.ht/~cedric/ip-link)
is to visualize the relationships between different IP from network traffic capture.

For reporting issues, visit the tracker here:
https://todo.sr.ht/~cedric/ip-link


## Installation

Python >= 3.8.

```bash
$ sudo apt install libpcap0.8
$ git clone https://git.sr.ht/~cedric/ip-link
$ cd ip-link/
$ poetry install
$ poetry shell
```

## Quick example

```bash
$ mkdir captures data
$ sudo tcpdump -p -i enp5s0 -s 0 -w captures/snif.pcap
$ ip-link/pcap_to_object.py -i captures/snif.pcap -o data/dic.pyobj
$ ip-link/object_to_graphviz.py -i ./data/dic.pyobj
$ dot -Tpng -o ./data/graphviz.png ./data/ip.dot
$ xdg-open ./data/graphviz.png &
```



## Tutorial and examples

You will find a complete tutorial
[here](https://ip-link.readthedocs.io/en/latest/tutorial.html).


## License

This software is licensed under
[GNU General Public License version 3](https://www.gnu.org/licenses/gpl-3.0.html).

Copyright (C) 2010-2022 [Cédric Bonhomme](https://www.cedricbonhomme.org).
