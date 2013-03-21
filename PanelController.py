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

class PanelController:
	maxroutes = 0
	routelen = 0

	serialport = 0

	def __init__(self, commpath):
		serialport = open(commpath, 'w')

	def show_route(self, id, color, heartbeat, holds):
		cmd = "%02d %d %d %d %d %d %d" % (CMD_SHOW_ROUTE, id, len(holds), color[0], color[1], color[2], heartbeat)
		for hold in holds:
			cmd += " %d" % (hold)
		cmd += "\n"

		print cmd

	def hide_route(self, id):
		print "%02d %d\n" % (CMD_HIDE_ROUTE, id)

	def set_brightness(self, brightness):
		print "%02d %d %d %d\n" % (CMD_SET_BRIGHTNESS, brightness[0], brightness[1], brightness[2])

	def get_brightness(self):
		print "%02d\n" % (CMD_GET_BRIGHTNESS)
		return (1, 1, 1)

	def get_capabilities(self):
		print "%02d\n" % (CMD_GET_CAPABILITIES)
		return (8, 20)

	def raw_touch(self):
		print "%02d\n" % (CMD_RAW_TOUCH_MODE)

	def get_rc_levels(self):
		print "%02d\n" % (CMD_GET_RC)
		return (1, 1, 1, 1, 1, 1)

	def set_rc_levels(self, levels):
		cmd = "%02d" % (CMD_GET_RC)
		for level in levels:
			cmd += " %d" % (level)
		cmd += "\n"
		
		print cmd




