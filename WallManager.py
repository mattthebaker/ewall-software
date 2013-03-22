#!/usr/bin/python

import sqlite3
import sys

class RouteSet:
    did = 0
    holds = []
    color = ()
    displayed = []
    heartbeat = 1
    change = 0

    def __init__(self, did, color):
        self.did = did
        self.color = color

class WallManager:
    controllers = []

    idpool = range(1, 255)
    colorpool = [(255, 255, 0), (0, 255, 255), (255, 0, 255)]

    activeroutes = []

    sql3conn = 0

    mode = "idle"

    ts = None
    st = None
                
    def __init__(self, dbpath):
        sql3conn = sqlite3.connect(dbpath)

        c = sql3conn.cursor()

        for row in c.execute('select * from controller;'):
            self.controllers.append(PanelController(row[0], row[2]))
            print row

    def show_route_byid(self, routeid, color=None):
        if not color:
            color = self.colorpool.pop(0)

        did = self.idpool.pop(0)

        c = self.sql3conn.cursor()

        for ctrlr in self.controllers:
            holds = []

            for row in c.execute('select rh.position '
                                 'from route_hold as rh, route as r '
                                 'where r.id = rh.route_id and r.id = ? '
                                 'and rh.controller_id = ?', routeid, ctrlr.cid):
                holds.append(row[0])

            if holds:
                ctrlr.show_route(did, color, 0, holds)
                self.activeroutes.append((routeid, did, color))

    def show_route_byname(self, name, color=None):
        c = self.sql3conn.cursor()

        for row in c.execute('select r.id from route as r where r.name = ?', name):
            show_route_byid(row[0], color)

    def random_route_bydifficulty(self, difficulty, color=None):
        c = self.sql3conn.cursor()

        c.execute('select r.id from route as r where r.difficulty = ?', difficulty)
        rows = c.fetchall()

        row = rows[random.randint(0, len(rows) - 1)]

        show_route_byid(row[0], color)

    def random_route_byhold(self, holdpos, cntrlrid, color=None):
        c = self.sql3conn.cursor()

        c.execute('select r.id from route as r, route_hold as rh '
                  'where r.id = rh.route_id and rh.position = ? '
                  'and rh.controller_id = ? ', holdpos, cntrlrid)
        
        rows = c.fetchall()
        row = rows[random.randint(0, len(rows) - 1)]

        show_route_byid(row[0], color)        
            
    def hide_route_byid(self, routeid):
        for r in activeroutes:
            if r[0] == routeid:
                route = r

        for cntrlr in self.controllers:
            cntrlr.hide_route(route[1])

        idpool.append(route[1])
        colorpool.append(route[2])

    def mode_touchtoggle_init(self):
        self.ts = RouteSet(self.idpool.pop(0), self.colorpool.pop(0))

    def mode_touchtoggle_exit(self):
        for ctrlr in self.controllers:
            ctrlr.hide_route(self.ts.did)
        self.idpool.append(self.ts.did)
        self.colorpool.append(self.ts.color)
        ts = None

    def run(self):
        touches = []

        c = self.sql3conn.cursor()
        
        while 1:
            for ctrlr in self.controllers:
                tc = ctrlr.get_touches()
                if tc:
                    for t in tc:
                        touches.append(t.insert(0, ctrlr.cid))

            if self.mode == "touchtoggle":
                if touches:
                    for tch in touches:
                        if tch[1]:
                            c.execute('select th.controller_id, th.position from touch_hold as th '
                                      'where th.controller_id = ? and th.touch_channel = ? '
                                      'and rc_level = ? ', tch[0], tch[2], tch[3])
                            hpos = c.fetchone()

                            ts.change = 1
                            if ts.holds.count(hpos):
                                ts.holds.remove(hpos)
                            else:
                                ts.holds.append(hpos)

                        touches.pop(0)
                        
                    if ts.change:
                        ts.change = 0
                        for ctrlr in self.controllers:
                            hlds = []
                            for h in ts.holds:
                                if h[0] == ctrlr.cid:
                                    hlds.append(h[1])
                            if hlds:
                                if not ts.displayed.count(ctrlr.cid):
                                    ts.displayed.append(ctrlr.cid)
                                    ctrlr.show_route(ts.did, ts.color, ts.heartbeat, hlds)
                                else:
                                    ctrlr.update_route(ts.did, ts.color, ts.heartbeat, hlds)

            if self.mode == "swtoggle":
                if not st:
                    st = RouteSet(idpool.pop(0), colorpool.pop(0))

            
                
            
        

wm = WallManager("ewall.db")
