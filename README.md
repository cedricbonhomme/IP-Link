# IP-Link

## Presentation

The goal of [IP-Link](https://github.com/cedricbonhomme/IP-Link)
is to visualize the relationships between different IP from network traffic capture.


## Installation

Python >= 3.9.

```bash
$ sudo apt install libpcap0.8
$ git clone https://github.com/cedricbonhomme/IP-Link
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


If you wish and if you like IP-Link, you can donate:

![GitHub Sponsors](https://img.shields.io/github/sponsors/cedricbonhomme)

Thank you !


## License

This software is licensed under
[GNU General Public License version 3](https://www.gnu.org/licenses/gpl-3.0.html).

Copyright (C) 2010-2024 [Cédric Bonhomme](https://www.cedricbonhomme.org).
