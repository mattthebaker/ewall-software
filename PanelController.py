#!/usr/bin/python

CMD_SHOW_ROUTE          = 0x01
CMD_HIDE_ROUTE          = 0x02
CMD_SET_BRIGHTNESS      = 0x03
CMD_GET_BRIGHTNESS      = 0x04
CMD_GET_HOLD            = 0x05
CMD_GET_CAPABILITIES    = 0x06
CMD_GET_TOUCHMAP        = 0x07
CMD_RETRAIN_TOUCHMAP    = 0x08
CMD_RAW_TOUCH_MODE      = 0x09
CMD_RESET               = 0x0a
CMD_GET_RC              = 0x0b
CMD_SET_RC              = 0x0c

CMD_SEND_BRIGHTNESS     = 0x04
CMD_SEND_HOLD           = 0x05
CMD_SEND_CAPABILITIES   = 0x06
CMD_SEND_TOUCHMAP       = 0x07
CMD_SEND_RAWTOUCH       = 0x09
CMD_SEND_RC             = 0x0b

import serial

class PanelController:

    def __init__(self, commpath, controllerid):
        self.ser = serial.Serial(commpath, 115200)
        self.cid = controllerid

        self.maxroutes = 0
        self.routelen = 0

        self.touches = []

    #    self.maxroutes, self.routelen = self.get_capabilities()
        self.raw_touch()

    def show_route(self, id, color, heartbeat, holds):
        if not holds:
            self.hide_route(id)
            return
        
        cmd = "%02d %d %d %d %d %d %d" % (CMD_SHOW_ROUTE, id, len(holds), color[0], color[1], color[2], heartbeat)
        for hold in holds:
            cmd += " %d" % (hold)
        cmd += "\n"

        self.ser.write(cmd)
        print cmd

    def update_route(self, id, color, heartbeat, holds):
        # for now, controller firmware checks for a matching id first when showing
        # and overwrites that route
        self.show_route(id, color, heartbeat, holds)

    def hide_route(self, id):
        self.ser.write("%02d %d\n" % (CMD_HIDE_ROUTE, id))

    def set_brightness(self, brightness):
        self.ser.write("%02d %d %d %d\n" % (CMD_SET_BRIGHTNESS, brightness[0], brightness[1], brightness[2]))
        
    def get_brightness(self):
        self.ser.write("%02d\n" % (CMD_GET_BRIGHTNESS))
        r = self.wait_response("%02d" % (CMD_SEND_BRIGHTNESS))
        r = map(int, r[3:].strip().split(' '))
        return r

    def get_capabilities(self):
        self.ser.write("%02d\n" % (CMD_GET_CAPABILITIES))
        r = self.wait_response("%02d" % (CMD_SEND_CAPABILITIES))
        r = map(int, r[3:].strip().split(' '))
        return r

    def get_touchmap(self):
        self.ser.write("%02d\n" % (CMD_GET_TOUCHMAP))
        r = self.wait_response("%02d" % (CMD_SEND_TOUCHMAP))
        r = map(int, r[3:].strip().split(' '))
        return r
        
    def raw_touch(self):
        self.ser.write("%02d\n" % (CMD_RAW_TOUCH_MODE))

    def get_rc_levels(self):
        self.ser.write("%02d\n" % (CMD_GET_RC))
        r = self.wait_response("%02d" % (CMD_SEND_RC))
        r = map(int, r[3:].strip().split(' '))
        return r

    def set_rc_levels(self, levels):
        cmd = "%02d" % (CMD_GET_RC)
        for level in levels:
            cmd += " %d" % (level)
        cmd += "\n"
        
        self.ser.write(cmd)

    def wait_response(self, cmdstr):
        while 1:
            cmd = self.ser.readline()
            if cmd.startswith(cmdstr):
                return cmd

    def check_buffer(self):
        while self.ser.inWaiting() > 0:
            print self.ser.readline(),

    def process_serial(self):
        while self.ser.inWaiting() > 0:
            self.handle_command(self.ser.readline())

    def handle_command(self, cmdstr):
        if cmdstr.startswith("%02d" % CMD_SEND_RAWTOUCH):
            print cmdstr[3:]
            self.touches.append(map(int, cmdstr[3:].split(' ')))

    def get_touches(self):
        self.process_serial()
        t = self.touches
        self.touches = []
        return t

