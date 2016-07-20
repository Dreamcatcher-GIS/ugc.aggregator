# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import MySQLdb
import uuid
from dao.SuperDAO import SuperDAO

class TuniuDAO(SuperDAO):

    def __init__(self, host, db, user, password):
        SuperDAO.__init__(self, host, db, user, password)

    def saveListPageInfo(self, listPageInfo):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            for hotel in listPageInfo:
                id = uuid.uuid1()
                cursor.execute("insert into tuniu_url(guid,url,city,comm_num)values(%s,%s,%s,%s)",(id,hotel['url'],hotel['city'],hotel['comm_num']))
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    def getAllUrl(self, city):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        urlList = []
        try:
            cursor.execute("select * from tuniu_url where city='%s'"%city)
            urlList = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return urlList

    def get_all_room_info(self):
        return self.get_records("tuniu_roominfo")

    def saveComments(self, commList):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            for commItem in commList:
                placeholders = ', '.join(['%s'] * len(commItem))
                columns = ', '.join(commItem.keys())
                sql = "insert into tuniu_comm( %s ) values ( %s )" % (columns, placeholders)
                cursor.execute(sql, commItem.values())
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    def saveHotelInfo(self, hotelItem):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            placeholders = ', '.join(['%s'] * len(hotelItem))
            columns = ', '.join(hotelItem.keys())
            sql = "insert into tuniu_hotelinfo( %s ) values ( %s )" % (columns, placeholders)
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
                sql = "insert into tuniu_roominfo( %s ) values ( %s )" % (columns, placeholders)
                cursor.execute(sql, room.values())
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    def get_hotel_comments(self):
        return self.get_records("tuniu_comm")

    def save_hotels_location(self, hotels_location):
        self.save_records("hotel_location", hotels_location)

    def get_hotelinfo(self):
        return self.get_records("tuniu_hotelinfo")

    '''
    获取评论类型以及对应的评论信息
    '''
    def get_comm_type_num(self, hotel_name):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        comm_type_num = []
        try:
            sql = '''
                    select temp1.comm_type,count(*) as comment_num from
                    (
                        select tuniu_comm.* from tuniu_comm,
                        (
                            select guid from tuniu_url where hotel_name='%s'
                        )temp
                        where tuniu_comm.hotel_id = temp.guid
                    )temp1
                    group by temp1.comm_type
                  '''
            cursor.execute(sql%hotel_name)
            comm_type_num = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return comm_type_num

    '''
    更新评论情感值
    '''
    def update_hotel_comm(self, records):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for record in records:
            try:
                sql = "update tuniu_comm set senti_value='%s',viewpoint='%s' where guid='%s'"
                cursor.execute(sql%(record["senti_value"], record["viewpoint"],record["guid"]))
            except Exception, e:
                print e
        db.commit()
        cursor.close()
        db.close()

    '''
    更新评论形容词统计
    '''
    def update_hotel_comm_word_freq(self, records):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for record in records:
            try:
                sql = "update tuniu_comm set word_freq='%s' where guid='%s'"
                cursor.execute(sql%(record["word_freq"], record["guid"]))
            except Exception, e:
                print e
        db.commit()
        cursor.close()
        db.close()

    '''
    根据酒店名称获取酒店评论
    '''
    def get_hotel_comments_by_name(self, hotel_name):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        hotel_comments = []
        try:
            sql = '''
                    select tuniu_comm.* from tuniu_comm,
                    (
                        select guid from tuniu_url where hotel_name='%s'
                    )temp
                    where tuniu_comm.hotel_id = temp.guid
                  '''
            cursor.execute(sql%hotel_name)
            hotel_comments = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return hotel_comments

    '''
    根据文本获取相关评论
    '''
    def get_hotel_comments_by_text(self, hotel_name, text):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        hotel_comments = []
        try:
            sql = '''
                    select tuniu_comm.* from tuniu_comm,
                    (
                        select guid from tuniu_url where hotel_name='%s'
                    )temp
                    where tuniu_comm.hotel_id = temp.guid and tuniu_comm.remark like '%%%s%%'
                  '''
            cursor.execute(sql%(hotel_name, text))
            hotel_comments = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return hotel_comments

    # 获得途牛酒店对应的guid
    def _returnbed(self,hotel_name):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        try:
            sql = '''
                    select tuniu_roominfo.* from tuniu_roominfo,
                    (
                        select guid from tuniu_url where hotel_name='%s'
                    )temp
                    where temp.guid = tuniu_roominfo.hotel_id
                  '''
            cursor.execute(sql%hotel_name)
            hotel_comments = cursor.fetchall()
            return hotel_comments
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    '''
    获取途牛中的所有评论
    '''
    def get_remarks(self):
        return self.get_records("tuniu_comm")
