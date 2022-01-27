#! /usr/bin/env python
# -*- coding: utf-8 -*-


import gobject

import dbus
import dbus.mainloop.glib


def sclick_signal_handler(node):
    global rtg
    for i in range(4):
        rtg.new_edge(node, {}, "%s%i" % (node, i), {})


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
control = bus.get_object("org.secdev.rtgraph3d", "/control")
control.connect_to_signal(
    "node_shift_click",
    sclick_signal_handler,
    dbus_interface="org.secdev.rtgraph3d.events",
)
rtg = dbus.Interface(control, "org.secdev.rtgraph3d.command")


loop = gobject.MainLoop()
loop.run()
