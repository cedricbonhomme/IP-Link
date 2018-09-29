IP-Link
=======

Presentation
------------

The goal of [IP-Link](https://ip-link.readthedocs.io)
([source code](https://gitlab.com/cedric/ip-link))
is to see the relationships between different IP from network traffic capture,
thus quickly for a given address with the IP that communicates the most.
IP-Link offers severall visualization methods.

Installation
------------

```bash
sudo apt install libpcap0.8 libpcap0.8-dev
pipenv install
pipenv shell
```

Requirements
------------

Python 2.7.

Python modules:

* [Pylibpcap](http://sourceforge.net/projects/pylibpcap/);
* [Pcapy](http://oss.coresecurity.com/projects/pcapy.html);
* [matplotlib](http://matplotlib.sourceforge.net/);
* [SQLite](http://sqlite.org) interface;
* [VPython](http://vpython.org/) for the Realtime Graph 3D visualization.

Software:

* [tcpdump](http://www.tcpdump.org/);
* [ploticus](http://ploticus.sourceforge.net/).


Turorial and examples
---------------------

The site of IP-Link provides a complete [tutorial](https://ip-link.readthedocs.io/en/latest/tutorial.html).


Contact
-------

[Cédric Bonhomme](https://www.cedricbonhomme.org)
