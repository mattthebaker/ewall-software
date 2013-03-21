#!/usr/bin/python

import sqlite3
import sys

class WallManager:
	controllers = []

	sql3conn = 0
	
	def __init__(self, dbpath):
		sql3conn = sqlite3.connect(dbpath)

		c = sql3conn.cursor()

		for row in c.execute('select * from controller;'):
			#controllers.append(PanelController(row[2]))
			print row


wm = WallManager(sys.argv[1])
