#!/usr/bin/python

import sqlite3
import sys
import socket
import select
import getopt
import random
import pickle

from PanelController import PanelController

class RouteSet:


    def __init__(self, did, color):
        self.did = did
        self.color = color
        
        self.holds = []
        self.displayed = []
        self.heartbeat = 1
        self.change = 0
        self.difficulty = ""
        self.name = ""

class WallManager:

                
    def __init__(self, dbpath):
        self.controllers = []

        self.idpool = range(1, 255)
        self.colorpool = [(255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 0 , 0), (0, 255, 0), (0, 0, 255)]

        self.activeroutes = []

        self.ts = None

        self.sock = None

        self.touchen = False
        self.randtouchen = False
        self.randtouchrid = None
        
        self.sql3conn = sqlite3.connect(dbpath)

        c = self.sql3conn.cursor()

        for row in c.execute('select * from controller;'):
            self.controllers.append(PanelController(row[2], row[0]))
            print row

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 48790))
        self.sock.listen(5)

    def show_route_byid(self, routeid, color=None):
        if not color:
            if len(self.colorpool):
                color = self.colorpool.pop(0)
            else:
                return

        if len(self.idpool):
            did = self.idpool.pop(0)
        else:
            return

        c = self.sql3conn.cursor()

        for ctrlr in self.controllers:
            holds = []

            for row in c.execute('select rh.position '
                                 'from route_hold as rh, route as r '
                                 'where r.id = rh.route_id and r.id = ? '
                                 'and rh.controller_id = ?', (routeid, ctrlr.cid,)):
                holds.append(row[0])
            if holds:
                ctrlr.show_route(did, color, 0, holds)
                self.activeroutes.append((routeid, did, color))

        return routeid

    def show_route_byname(self, name, color=None):
        c = self.sql3conn.cursor()

        for row in c.execute('select r.id from route as r where r.name = ?', name):
            show_route_byid(row[0], color)

    def random_route_bydifficulty(self, difficulty, color=None):
        c = self.sql3conn.cursor()

        c.execute("select r.id from route as r where r.difficulty = ?", (difficulty,))
        rows = c.fetchall()

        row = rows[random.randint(0, len(rows) - 1)]

        self.show_route_byid(row[0], color)

    def random_route_byhold(self, holdpos, cntrlrid, color=None):
        if self.randtouchrid:
            self.hide_route_byid(self.randtouchrid)
            self.randtouchrid = None
            
        c = self.sql3conn.cursor()

        c.execute('select r.id from route as r, route_hold as rh '
                  'where r.id = rh.route_id and rh.position = ? '
                  'and rh.controller_id = ? ', (holdpos, cntrlrid,))
        
        rows = c.fetchall()
        row = rows[random.randint(0, len(rows) - 1)]

        self.randtouchrid = self.show_route_byid(row[0], color)        
            
    def hide_route_byid(self, routeid):
        for r in self.activeroutes:
            if r[0] == routeid:
                route = r

        for cntrlr in self.controllers:
            cntrlr.hide_route(route[1])

        self.idpool.append(route[1])
        self.colorpool.append(route[2])

    def hide_route_all(self):
        for rid, did, color in self.activeroutes:
            self.hide_route_byid(rid)
        self.activeroutes = []

    def mode_touchtoggle_init(self):
        self.ts = RouteSet(self.idpool.pop(0), self.colorpool.pop(0))

    def mode_touchtoggle_exit(self):
        if self.ts:
            for ctrlr in self.controllers:
                ctrlr.hide_route(self.ts.did)
            self.idpool.append(self.ts.did)
            self.colorpool.append(self.ts.color)
            self.ts = None

    def rs_toggle_hold(self, hpos):
        if self.ts:
            self.ts.change = 1
            if self.ts.holds.count(hpos):
                self.ts.holds.remove(hpos)
            else:
                self.ts.holds.append(hpos)

    def rs_refresh_display(self):
        if self.ts and self.ts.change:
            self.ts.change = 0
            for ctrlr in self.controllers:
                hlds = []
                for h in self.ts.holds:
                    if h[0] == ctrlr.cid:
                        hlds.append(h[1])
#                if hlds:
                if not self.ts.displayed.count(ctrlr.cid):
                    self.ts.displayed.append(ctrlr.cid)
                    ctrlr.show_route(self.ts.did, self.ts.color, self.ts.heartbeat, hlds)
                else:
                    ctrlr.update_route(self.ts.did, self.ts.color, self.ts.heartbeat, hlds)

    def rs_clear(self):
        if self.ts:
            if len(self.ts.holds) > 0:
                self.ts.holds = []
                self.ts.change = 1

        self.rs_refresh_display()
            
                        
    def save_route(self):
        if self.ts:
            c = self.sql3conn.cursor()

            c.execute('insert into route (name, difficulty) values (?, ?)', (self.ts.name, self.ts.difficulty,))
            routeid = c.lastrowid

            for cid, hpos in self.ts.holds:
                c.execute('insert into route_hold (route_id, controller_id, position) values (?, ?, ?)',
                          (routeid, cid, hpos,))
            
            self.sql3conn.commit()

            return routeid
        

    def parse_command(self, cmd):
        random, touch, difficulty = 0, 0, 0
        optlist, args = getopt.getopt(cmd, 'rtV:isn:dhgc')
        for o, a in optlist:
            if o == "-r":
                random = 1
                
            elif o == "-t":
                self.touchen = True
                if random:
                    self.randtouchen = True

            elif o == "-V":
                difficulty = "V" + a
                if not random and self.ts:
                    self.ts.difficulty = difficulty
                if random:
                    self.random_route_bydifficulty(difficulty)

            elif o == "-i":
                if self.ts:
                    self.mode_touchtoggle_exit()
                self.mode_touchtoggle_init()
                self.ts.heartbeat = 0

            elif o == "-s":
                if self.randtouchen:
                    self.randtouchen = False
                    self.touchen = False
                else:
                    self.save_route()
                    if self.ts:                     # should remove ts from memory and redisplay route in same color instead
                        self.ts.heartbeat = 0
                        self.ts.change = 1
                        self.rs_refresh_display()

            elif o == "-n":
                if self.ts:
                    self.ts.name = a

            elif o == "-d":
                if self.randtouchen:
                    if self.randtouchrid:
                        self.hide_route_byid(self.randtouchrid)
                        self.randtouchrid = None
                    self.randtouchen = False
                    self.touchen = False
                else:
                    self.mode_touchtoggle_exit()

            elif o == "-h":
                if len(args) > 1:
                    self.rs_toggle_hold(map(int, (args[0], args[1])))
                    self.rs_refresh_display()

            elif o == "-g":
                if self.ts:
                    self.mode_touchtoggle_exit()
                self.mode_touchtoggle_init()
                self.ts.heartbeat = 0

            elif o == "-c":
                if self.ts:
                    self.rs_clear()
                else:
                    self.hide_route_all()
        

    def run(self):
        touches = []

        c = self.sql3conn.cursor()
        
        while 1:
            for ctrlr in self.controllers:
                tc = ctrlr.get_touches()
                if tc:
                    for t in tc:
                        t.insert(0, ctrlr.cid)
                        print t
                        touches.append(t)

            sel = select.select([self.sock], [], [], 0)
            for s in sel[0]:
                conn = self.sock.accept()[0]
                cmd = conn.recv(1024)
                conn.close()
                cmd = pickle.loads(cmd)
                print "Received Command:"
                print cmd
                self.parse_command(cmd)

            if self.touchen:
                if touches:
                    hpos = []
                    for tch in touches:
                        if tch[1]:
                            c.execute('select th.controller_id, th.position from touch_hold as th '
                                      'where th.controller_id = ? and th.touch_channel = ? '
                                      'and rc_level = ? ', (tch[0], tch[2], tch[3],))
                            row = c.fetchone()
                            if row:
                                hpos.append(row)

                        touches.pop(0)

                    for cid, pos in hpos:
                        if self.randtouchen:
                            self.random_route_byhold(pos, cid)
                        else:
                            self.rs_toggle_hold((cid, pos))

                    if not self.randtouchen:
                        self.rs_refresh_display()
            else:
                touches = []

            
           
if sys.argv[1] == "-S":
    wm = WallManager("ewall.db")
    wm.run()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 48790))
##cmd = ""
##for i in range(1, len(sys.argv) - 1):
##    cmd += sys.argv[i] + " "
##cmd += sys.argv[-1]
##sock.sendall(cmd)
sock.sendall(pickle.dumps(sys.argv[1:]))
sock.close()
