# -*- coding: utf-8 -*-
__author__ = 'LiuYang'
import MySQLdb
import uuid
import random
import json

from dao.SuperDAO import SuperDAO


class xiechengDAO(SuperDAO):

    def __init__(self, host, db, user, password):
        SuperDAO.__init__(self, host, db, user, password)

    # 存储酒店基本信息
    def savehotelComment(self,items):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for item in items:
            try:
                cursor.execute("replace into hotelinfo(guid,city,title,price,score,recommend,area,havawifi,discussNum,common_facilities,activity_facilities,service_facilities,room_facilities)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" ,(item["guid"],item["city"],item["title"],item["price"],item["score"],item["recommend"],item["area"],item["havawifi"],item["discussNum"],item["common_facilities"],item["activity_facilities"],item["service_facilities"],item["room_facilities"]))
            except Exception, e:
                print e
            db.commit()
        cursor.close()
        db.close()


    # 存储所有酒店的链接
    def savehotellink(self,listPageInfo):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for hotel in listPageInfo:
            try:
                    id = uuid.uuid1()
                    cursor.execute("replace into hotellianjie(guid,lianjie,city,comm_num)values(%s,%s,%s,%s)" ,(id,hotel["url"],hotel["city"],hotel["comm_num"]))
            except Exception,e:
                print hotel["url"]
        db.commit()
        cursor.close()
        db.close()

    # 取出周围设施数据
    def get_around_facilities_data(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("SELECT facilities_lntandlang FROM around_facilities_distance")
        data = []
        rows = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        for i in rows:
            data.append(json.loads(i[0]))
        return data



    # 取出周围设施中最远距离的设施和距离
    def get_max_distance_data(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("SELECT maxdistance FROM around_facilities_distance")
        data = []
        rows = cursor.fetchall()

        for i in rows:
            data.append(json.loads(i[0]))
        return data
        db.commit()
        cursor.close()
        db.close()

    # 从数据库中读取链接数据
    def _return(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()

        cursor.execute("SELECT * FROM hotellianjie")

        rows = cursor.fetchall()
        return rows

        db.commit()
        cursor.close()
        db.close()


    # 从数据库中读取评论数据
    def _returncommentinfo(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()

        cursor.execute("SELECT * FROM hotelcommentinfo")

        rows = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return rows

    # 存储酒店评论信息
    def savehotelCommentinfo(self,items):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for item in items:

            try:
                cursor.execute("insert into hotelcommentinfo(hotelname,username,commentscore,intime,tourstyle,praisenum,commenttime,comment)values(%s,%s,%s,%s,%s,%s,%s,%s)" ,(item["title"],item["username"],item["commentscore"],item["intime"],item["tourstyle"],item["praisenum"],item["commenttime"],item["comment"]))
            except :
                print item
        db.commit()
        cursor.close()
        db.close()

    # 存储酒店评论信息(含好感度)
    def savehotelCommentinfosenti(self,items):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for item in items:

            try:
                cursor.execute("insert into xiechengcomment(hotelname,username,commentscore,intime,tourstyle,praisenum,comment,senti_value,viewpoint)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)" ,(item["hotelname"],item["username"],item["commentscore"],item["intime"],item["tourstyle"],item["praisenum"],item["comment"],item["senti_value"],item["viewpoint"]))
            except Exception,e:
                print e
        db.commit()
        cursor.close()
        db.close()


    # 从数据库中读取评论数据
    def _returncomment(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM hotelcommentinfo")
        rows = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return rows

    def get_comments(self):
        return self.get_records("xiechengcomment")