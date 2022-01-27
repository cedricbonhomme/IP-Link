.. IP-Link documentation master file, created by
   sphinx-quickstart on Wed Jul 25 18:04:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IP-Link's documentation!
===================================

.. image:: _static/images/logo.png
   :align: right

The goal of `IP-Link <https://sr.ht/~cedric/ip-link>`_ is to show the
relationships between different IP addresses from network traffic capture,
thus quickly determining for a given address the IP address with which it
communicates the most.


Installation
============

.. code-block:: bash

    $ sudo apt install libpcap0.8
    $ git clone https://git.sr.ht/~cedric/ip-link
    $ cd ip-link/
    $ poetry install
    $ poetry shell


How it works
============

This section exposes the principles of IP-Link.

.. toctree::
    :maxdepth: 2

    how-it-works


Tutorial
========

This section explains how to generate the different visualizations.

.. toctree::
    :maxdepth: 2

    tutorial


Documentation
=============

This section explains how to use the different components.

.. toctree::
    :maxdepth: 2

    documentation


Donation
========

If you wish and if you like IP-Link, you can donate via bitcoin.
My bitcoin address: 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ.
Thank you!

.. image:: _static/images/BC_Rnd_48px.png
    :target: http://wiki.cedricbonhomme.org/projects
