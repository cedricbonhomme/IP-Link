How it works
============

This page explain the process of the data extraction of the captured traffic.

Extraction of the data
======================

Ways of data extraction
-----------------------

Diagramme1.png

We can see that pcap_to_sqlite.py, pcap_to_sqlite1.py and pcap_to_sqlite.sh are three alternatives
to generate the SQLite base. So, it is not necessary to use Python (although recommended) to
generate the base. Once the base created, a Python script or anything other programming language
can easily examine it.

Storing the results of extraction
---------------------------------

SQLite base
~~~~~~~~~~~

It is possible to store the extraction results (in this case timestamp, source and destination IP) in a database.

Python serialized object
~~~~~~~~~~~~~~~~~~~~~~~~

Structure of the Python serialized object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> dic_ip = {'212.110.251.3' : {'212.110.251.5' : 20, '212.110.251.12' : 16,
                                    '212.112.245.2' : 451},
                '212.112.245.2' : {'212.110.251.3' : 48, '80.114.227.3' : 2},
                .
                .
                .
            }

Some tests
^^^^^^^^^^

.. code-block:: python

    >>> import pickle
    >>> dic_obj = open("./dic.pyobj", "r")
    >>> dic_ip = pickle.load(dic_obj)
    >>> for i in dic_ip['212.110.251.3']:
                a += dic_ip['212.110.251.3'][i]
    >>> print a
    2815911
    >>> len(dic_ip['212.110.251.3'])
    893436


We see here that 212.110.251.3 has contacted 738,585 different IP, for a total of 2,815,911 contacts.

.. code-block:: python

    >>> (len(dic_ip['212.110.251.3'])/(len(dic_ip)*1.0))
    18.037144671290417


This already represents a significant part of sources ip.

.. code-block:: python

    >>> liste = dic_ip['212.110.251.3'].items() # list of IP contacted by 212.110.251.3
    >>> liste.sort(key = operator.itemgetter(1), reverse = True)
    >>> liste[0]
    ('69.16.172.40', 204909) # most contacted by 212.110.251.3
    >>> liste[1]
    ('149.20.20.133', 114881)
    >>> liste[-1]
    ('83.9.4.233', 1) # less contacted by 212.110.251.3

    >>> liste[-43527]
    ('83.9.122.249', 1)
    >>> liste[-43528]
    ('206.1.38.179', 2)


212.110.251.3 has contacted 43,527 different IP one time.

What can we do with this object ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So we have seen that this is very simple to deal with this object to obtain what we want. This object represent the part of the base that you want to exploit.
It can be created with sqlite_to_object.py. Remember that the SQLite base contains all the informations of the Pcap. So, if you want, you can filter these informations before visualizing.
For example :

.. code-block:: bash

    cedric@debian:~/IP-Link/source$ python sqlite_to_object.py -i data/ip.sql -r time -p 2009-1-15-22-00-00:2009-1-16-02-00-00
    DB connect
    Request sent to the base :
        SELECT ip_src, ip_dst FROM ip_link WHERE tts >= 1232053200.0 AND tts <=  1232067600.0
    Creating object...
    Reading the result of the query...
    Serialization...

Here, you will extract all the trafic between 2009/01/15 22h00m00s and 2009/01/16 02h00m00s. Now, for example you can generate the Circos matrix and a MooWheel graph :

.. code-block:: bash

    cedric@debian:~/IP-Link/source$ python object_to_circos.py -i jub-dic.pyobj -o ip.circos
    Loading objet...
    Searching IP that are source and destination...
    Circos matrix generation...
    Saving the matrix...

    cedric@debian:~/IP-Link/source$ python object_to_moowheel.py
    Loading dictionary...
    Creating MooWheel file...
    Writting file.

    
Visualization
=============