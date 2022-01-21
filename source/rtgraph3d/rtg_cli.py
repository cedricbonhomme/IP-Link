#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, dbus
import cmd

import warnings

warnings.filterwarnings("ignore", "tempnam", RuntimeWarning, __name__)


class Interp(cmd.Cmd):
    prompt = "RTG> "

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.last_selection = []
        try:
            self.bus = dbus.SessionBus()
            self.control = self.bus.get_object("org.secdev.rtgraph3d", "/control")
            self.rtg = dbus.Interface(self.control, "org.secdev.rtgraph3d.command")
        except dbus.DBusException as e:
            print("DBUS ERROR: %s" % e, file=sys.stderr)
            raise SystemExit

    def completedefault(self, text, line, begidx, endidx):
        l = self.rtg.get_all_nodes()
        return [n for n in l if n.startswith(text)]

    def do_quit(self, args):
        return True

    def do_edge(self, args):
        e = args.split()
        for n1, n2 in zip(e[:-1], e[1:]):
            self.rtg.new_edge(n1, {}, n2, {})

    def do_glow(self, args):
        for n in args.split():
            self.rtg.glow(n)

    def do_unglow(self, args):
        nodes = args.split()
        if nodes:
            for n in nodes:
                self.rtg.unglow(n)
        else:
            self.rtg.unglow_all()

    def do_find(self, args):
        a, v = [x.strip() for x in args.split("=")]
        self.last_selection = r = self.rtg.find(a, v)
        print("Found %i nodes" % len(r))
        for n in r:
            self.rtg.glow(n)

    def do_toggle(self, args):
        nodes = args.split()
        if not nodes:
            nodes = self.last_selection
        for n in nodes:
            self.rtg.toggle(n)

    def do_dotty(self, args):
        dot = self.rtg.get_dot()
        fname = os.tempnam()
        open(fname, "w").write(dot)
        os.spawnlp(os.P_NOWAIT, "dotty", "dotty", fname)

    def do_set_attraction(self, args):
        self.rtg.set_attraction(float(args))

    def do_set_repulsion(self, args):
        self.rtg.set_repulsion(float(args))

    def do_set_ambient(self, args):
        self.rtg.set_ambient(float(args))

    def do_remote_dump(self, args):
        self.rtg.file_dump(args)

    def do_remote_load(self, args):
        self.rtg.file_load(args)

    def do_reset(self, args):
        self.rtg.reset_world()

    def do_rotate(self, args):
        if args:
            r = float(args)
        else:
            r = 0.0
        self.rtg.auto_rotate_scene(r)

    def do_rotate_stop(self, args):
        self.rtg.stop_auto_rotate_scene()

    def do_update(self, args):
        node, val = args.strip().split(" ", 1)
        k, v = val.strip().split("=")
        k = k.strip()
        v = v.strip()
        if k in ["color", "radius", "pos"]:
            v = eval(v)
        self.rtg.update_node(node, {k: v})


if __name__ == "__main__":
    try:
        import readline, atexit
    except ImportError:
        pass
    else:
        histfile = os.path.join(os.environ["HOME"], ".rtg_cli_history")
        atexit.register(readline.write_history_file, histfile)
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass

    interp = Interp()
    while 1:
        try:
            interp.cmdloop()
        except KeyboardInterrupt:
            print()
        except Exception as e:
            l = str(e).strip()
            if l:
                print("ERROR: %s" % l.splitlines()[-1], file=sys.stderr)
            continue
        break
