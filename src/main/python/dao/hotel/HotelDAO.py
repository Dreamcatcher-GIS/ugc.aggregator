# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import traceback
import MySQLdb

from dao.SuperDAO import SuperDAO


class HotelDAO(SuperDAO):

    def __init__(self, host, db, user, password):
        SuperDAO.__init__(self, host, db, user, password)

    def get_baseinfo(self, city, OTA):
        result_data = []
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute("select * from baseinfo,location where location_id=location.guid and OTA='%s' and city='%s'"%(OTA, city))
            result_data = cursor.fetchall()
        except:
            traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return result_data

    def update_baseinfo(self, items):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for item in items:
            try:
                sql = '''
                      update baseinfo
                      set url='%s',location_id='%s',OTA='%s',comm_num='%s',if_overtime='%s',incre_num='%s'
                      where guid='%s'
                      '''
                cursor.execute(sql%(item["url"], item["location_id"], item["OTA"], item["comm_num"], item["if_overtime"],item["incre_num"], item["guid"]))
            except:
                traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()

    def save_baseinfo(self, records):
        self.save_records("baseinfo", records)

    def save_locations(self, records):
        self.save_records("location", records)

    def get_locations(self, city):
        result_data = []
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = '''
                  select * from location where city = '%s'
                  '''
            cursor.execute(sql%(city))
            result_data = cursor.fetchall()
        except:
            traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return result_data