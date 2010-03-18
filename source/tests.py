#! /usr/local/bin/python
#-*- coding: utf-8 -*-

"""tests

These classes perform different tests on the modules.
Can take some times...
"""

import unittest

import os
import pickle
import sqlite3
import operator

# module à tester
import pcap_to_sqlite
import pcap_to_sqlite1
import pcap_to_object
import pcap_to_object1
import sqlite_to_object


class PcapToSqliteTest(unittest.TestCase):
    """SQLite Tests."""
    def setUp(self):
        self.sqlite1 = pcap_to_sqlite.pcap_to_sqlite('./captures/capture.cap',\
                                                     './data/ip1.sql')
        self.sqlite2 = pcap_to_sqlite1.pcap_to_sqlite('./captures/capture.cap',\
                                                     './data/ip2.sql')
        #self.sqlite3 = os.system('pcap_to_sqlite.sh ./captures/capture.cap')

    def test_base(self):
        conn1 = sqlite3.connect("./data/ip1.sql", isolation_level = None)
        liste1 = conn1.execute("SELECT * FROM ip_link").fetchall()

        conn2 = sqlite3.connect("./data/ip2.sql", isolation_level = None)
        liste2 = conn2.execute("SELECT * FROM ip_link").fetchall()

        #conn3 = sqlite3.connect("./data/ip.sql", isolation_level = None)
        #liste3 = conn3.execute("SELECT * FROM ip_link").fetchall()

        self.assertEqual(len(liste1), len(liste2))
        #self.assertEqual(len(liste2), len(liste3))


class PcapToObjectTest(unittest.TestCase):
    """Test on the serialized object."""
    def setUp(self):
        pcap_to_object1.pcap_to_object('./captures/capture.cap',\
                                        './data/dic1.pyobj')
        pcap_to_object1.pcap_to_object('./captures/capture.cap',\
                                        './data/dic2.pyobj')
        obj1 = open("./data/dic1.pyobj", "r")
        self.dic1 = pickle.load(obj1)
        obj2 = open("./data/dic2.pyobj", "r")
        self.dic2 = pickle.load(obj2)

    def test_destination(self):
        self.assertEqual(self.dic1['65.185.106.105'], \
                        self.dic2['65.185.106.105'])

        self.assertEqual(self.dic1['65.185.106.105'], \
                        self.dic2['65.185.106.105'])
                        
        self.assertEqual(self.dic1, self.dic2)

    def test_contacte(self):
        """Contacted IP"""
        liste1 = self.dic1['192.168.1.2'].items()
        liste1.sort(key = operator.itemgetter(1), reverse = True)
        liste2 = self.dic2['192.168.1.2'].items()
        liste2.sort(key = operator.itemgetter(1), reverse = True)

        self.assertEqual(liste1[0], liste2[0])
        self.assertEqual(liste1[-1], liste2[-1])

        self.assertEqual(liste1, liste2)


if __name__ == '__main__':
    # Point of entry in execution mode.
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PcapToSqliteTest))
    suite.addTest(unittest.makeSuite(PcapToObjectTest))
    unittest.TextTestRunner(verbosity = 2).run(suite)
