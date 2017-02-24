# -*- coding:utf-8 -*-

import MySQLdb
from dao.SuperDAO import SuperDAO

class PmsDAO(SuperDAO):
    def __init__(self, host, db, user, password):
        SuperDAO.__init__(self, host, db, user, password)
    '''
    0 依据酒店名 查询其（baseinfo和location） hotelid
    '''
    def query_hotelid_from_hotelname(self,name):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        records = []
        try:
            cursor.execute("SELECT guid FROM baseinfo WHERE location_id in (SELECT guid FROM location WHERE hotel_name = '%s')"%(name))
            records = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return records
    '''
    0更新remark表中的 roomid
    '''
    def update_roomid(self,records):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for record in records:
            try:
                sql = "update remark set roomid='%s' where guid='%s'"
                cursor.execute(sql%(record["roomid"],record["guid"]))
            except Exception, e:
                print e
        db.commit()
        cursor.close()
        db.close()
    '''
    0获取到某一表的某一列
    '''
    def get_column_table(self,column,tablename):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        records = []
        try:
            cursor.execute("select %s from %s group by %s"%(column,tablename,column))
            records = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return records

    '''
    0 获取到 某表 中 某条件下的 某一列
    '''
    def get_condition_column(self,column,tablename,condition):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        records = []
        try:
            cursor.execute("select %s from %s where %s"%(column,tablename,condition))
            records = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return records
    '''
    更新 roominfo 表的 viewpoint
    '''
    def updata_roominfo_viewpoint(self,viewpoint,roomid):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "update roominfo set viewpoint = '%s' where roomid='%s'"%(viewpoint,roomid)
            cursor.execute(sql)
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    '''
    1店员登录 经理登录
    '''
    def user_login(self,username):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "select * from userinfo viewpoint = '%s' where roomid='%s'" %roomid
            cursor.execute(sql)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    1添加顾客入住信息
    '''
    def add_record(self,roomid,guestid,intime,outtime,charge):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "insert into roomrecord (roomid,guestid,intime,outtime,charge) values ('%s','%s','%s','%s','%s')"%(roomid,guestid,intime,outtime,charge)
            cursor.execute( sql )
            cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        pass
    '''
    1 顾客入住，修改roominfo表
    '''
    def alter_roominfo(self,roomid,guestid):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "update roominfo set guestid ='%s',roomstate='3' WHERE roomid = '%s'"%(guestid,roomid)
            cursor.execute(sql())
            pass
        except Exception,e:
            print e
        db.commit()
        cursor.close()
        db.close()
        pass

    '''
    1获取到某guest的所有remark
    '''
    def get_guest_remark(self,guestname):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "select * from remark where username='%s'" %guestname
            cursor.execute(sql)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    1获取到 酒店的 remark , 南京苏宁威尼斯酒店
    '''
    def get_hotel_remark(self,hotel_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "select * from remark where baseinfo_id ='%s'" %hotel_id
            cursor.execute(sql)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data
        pass

    '''
    1 依据楼层号 提取出 rooms
    '''
    def get_hotel_rooms(self,floornum):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "SELECT * FROM roominfo where floornum = '%s'" %floornum
            cursor.execute(sql)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data
    pass

