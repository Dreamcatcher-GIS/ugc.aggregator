# -*- coding: utf-8 -*-
__author__ = 'LiuYang'

import MySQLdb
import uuid
import traceback

from dao.SuperDAO import SuperDAO


class WeiboDAO(SuperDAO):

    def __init__(self, host, db, user, password):
        SuperDAO.__init__(self, host, db, user, password)

    # 存储微博id
    def saveWeiboID(self,weiboIDSet,userID,pageNum):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for weiboID in weiboIDSet:
            cursor.execute("insert into weibo_id(guid,userID,weiboID,pageNum)values(%s,%s,%s,%s)" ,(uuid.uuid1(),userID,weiboID,pageNum))
            db.commit()
        cursor.close()
        db.close()

    # 存储微博评论
    def saveWeiboComment(self,items):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        for item in items:
            try:
                cursor.execute("insert into weibo_comment(guid,userID,weiboID,pageNum,commPeople,commentText,commentTime,crawlTime,likeNum)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)" ,(uuid.uuid1(),item["userID"],item["weiboID"],item["pageNum"],item["commPeople"],item["commentText"],item["commentTime"],item["crawlTime"],item["likeNum"]))
            except:
                continue
            db.commit()
        cursor.close()
        db.close()

    # 获取api账号数量
    def countweiboaccountnumber(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("select count(*) from api_account")
        data = cursor.fetchone()
        cursor.close()
        db.close()
        return data

    #从mysql中获取微博账号
    def get_weibo_accounts(self):
        weibo_accounts = None
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute("select * from api_account")
            weibo_accounts = cursor.fetchall()
        except:
            print traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return weibo_accounts

    def saveWeibo_ByAPI(self,weiboid,text,lat,lon,title,userid,location,userdecription,gender,created_at,fax,localcity,formatted):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("insert into weibo_content(weiboid,text,lat,lon,title,userid,location,userdescription,gender,created_at,fax,locality,formatted)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   ,(weiboid,text,lat,lon,title,userid,location,userdecription,gender,created_at,fax,localcity,formatted))
        db.commit()
        cursor.close()
        db.close()

    '''
    获取地址
    '''
    def get_location(self, city):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        location = None
        try:
            cursor.execute("select * from city_location where city='%s'"%city)
            location = cursor.fetchone()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return location

    def save_location(self, location):
        self.save_record("city_location", location)