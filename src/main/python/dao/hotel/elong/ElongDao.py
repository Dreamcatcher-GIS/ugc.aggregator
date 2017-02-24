# -*- coding:utf-8 -*-
__author__ = 'pengshaowei'

import MySQLdb
from dao.SuperDAO import SuperDAO

class ElongDAO(SuperDAO):
	def __init__(self, host, db, user, password):
		SuperDAO.__init__(self, host, db, user, password)

	def getAllUrl(self):
		db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
		cursor = db.cursor()
		urlList = []
		try:
			cursor.execute("select * from baseinfo")
			urlList = cursor.fetchall()
		except Exception, e:
			print e
		db.commit()
		cursor.close()
		db.close()
		return urlList

	def saveHotelInfo(self, hotelItem):
		db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
		cursor = db.cursor()
		try:
			placeholders = ', '.join(['%s'] * len(hotelItem))
			columns = ', '.join(hotelItem.keys())
			sql = "insert into elong_hotelinfo( %s ) values ( %s )" % (columns, placeholders)
			cursor.execute(sql, hotelItem.values())
		except Exception, e:
			print e
		db.commit()
		cursor.close()
		db.close()

	def save_room_info(self, room_list):
		db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
		cursor = db.cursor()
		try:
			for room in room_list:
				placeholders = ', '.join(['%s'] * len(room))
				columns = ', '.join(room.keys())
				sql = "insert into elong_roominfo( %s ) values ( %s )" % (columns, placeholders)
				cursor.execute(sql, room.values())
		except Exception, e:
			print e
		db.commit()
		cursor.close()
		db.close()

	def saveComments(self, commList):
		db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
		cursor = db.cursor()
		try:
			for commItem in commList:
				placeholders = ', '.join(['%s'] * len(commItem))
				columns = ', '.join(commItem.keys())
				sql = "insert into remark ( %s ) values ( %s )" % (columns, placeholders)
				cursor.execute(sql, commItem.values())
		except Exception, e:
			print e
		db.commit()
		cursor.close()
		db.close()