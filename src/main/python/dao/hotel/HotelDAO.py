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
                      set url='%s',location_id='%s',OTA='%s',comm_num='%s',if_overtime='%s',incre_num='%s',img='%s'
                      where guid='%s'
                      '''
                cursor.execute(sql%(item["url"], item["location_id"], item["OTA"], item["comm_num"], item["if_overtime"],item["incre_num"], item["img"],item["guid"]))
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

    '''
    保存评论
    '''
    def save_remarks(self, records):
        self.save_records("remark",records)

    '''
    获取所有评论
    '''
    def get_remarks(self):
        return self.get_records("remark")

    def get_remarks_by_baseinfo_id(self, baseinfo_id):
        result_data = []
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "select * from remark where baseinfo_id = '%s'"
            cursor.execute(sql%baseinfo_id)
            result_data = cursor.fetchall()
        except:
            traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    更新评论
    '''
    def update_remarks(self, records):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for record in records:
            if record["senti_value"] is None:
                continue
            try:
                sql = "update remark set senti_value='%s',viewpoint='%s' where guid='%s'"
                cursor.execute(sql % (record["senti_value"], record["viewpoint"], record["guid"]))
            except Exception, e:
                print record
                print e
        db.commit()
        cursor.close()
        db.close()

    '''
    通过酒店名获取所有baseinfo
    '''
    def get_baseinfo_by_hotelname(self, hotelname, city):
        result_data = []
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = '''
                  select baseinfo.* from baseinfo,
                  (
                      select * from location where hotel_name='%s' and city = '%s'
                  )temp1
                  where baseinfo.location_id = temp1.guid
                  '''
            cursor.execute(sql % (hotelname, city))
            result_data = cursor.fetchall()
        except:
            traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    通过位置id获取所有baseinfo
    '''
    def get_baseinfo_by_location_id(self, location_id):
        result_data = []
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = '''
                  select * from baseinfo where location_id = '%s'
                  '''
            cursor.execute(sql % location_id)
            result_data = cursor.fetchall()
        except:
            traceback.print_exc()
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    根据评论类型进行评论数量统计
    '''
    def get_comm_type_statics(self, baseinfo_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        comm_type_num = []
        try:
            sql = '''
                    select remark.comm_type,count(*) as comment_num from remark
                    where remark.baseinfo_id = '%s'
                    group by remark.comm_type
                  '''
            cursor.execute(sql % baseinfo_id)
            comm_type_num = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return comm_type_num

    '''
    根据评论分数进行评论数量统计
    '''
    def get_comm_score_statics(self, baseinfo_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        comm_type_num = []
        try:
            sql = '''
                    select comm_score,count(*) as comment_num from remark
                    where baseinfo_id = '%s'
                    group by remark.comm_score
                  '''
            cursor.execute(sql % baseinfo_id)
            comm_type_num = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return comm_type_num

    def get_hotel_name_by_location_id(self, location_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = "select * from location where guid='%s'"
            cursor.execute(sql % location_id)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    def get_location_info_by_baseinfo_id(self, baseinfo_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = '''
                    SELECT location.* FROM location,
                    (
                        SELECT location_id FROM baseinfo WHERE baseinfo.guid = '%s'
                    )temp1
                    WHERE location.guid = temp1.location_id
                  '''
            cursor.execute(sql % baseinfo_id)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    def update_hotel_comm_word_freq(self, records):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        for record in records:
            try:
                sql = "update remark set word_freq='%s' where guid='%s'"
                cursor.execute(sql % (record["word_freq"], record["guid"]))
            except Exception, e:
                print e
        db.commit()
        cursor.close()
        db.close()

    def get_hotel_trace_users(self, baseinfo_id):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        user_list = []
        try:
            sql = '''
                    select remark.username from remark,
                    (
                        select DISTINCT(username) as username from remark
                        where baseinfo_id='%s'
                        and username != '艺龙网用户'
                        and username not like '%%**%%'
                    )temp1
                    where remark.username = temp1.username
                    group by remark.username
                    having count(*)>2
                  '''
            cursor.execute(sql % baseinfo_id)
            user_list = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return user_list

    def get_remarks_by_username(self, username):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = '''
                    select temp1.*,location.hotel_name,location.x,location.y  from baseinfo,location,
                    (
                        select * from remark where username='%s'
                    )temp1
                    where temp1.baseinfo_id = baseinfo.guid and baseinfo.location_id = location.guid
                    order by comm_time
                  '''
            cursor.execute(sql % username)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    def get_user(self, user_name):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = '''
                    SELECT * from location,baseinfo,
                    (
                        SELECT * FROM `user` WHERE user_name='%s'
                    )temp1
                    WHERE temp1.location_id = location.guid AND location.guid = baseinfo.location_id
                  '''
            cursor.execute(sql % user_name)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    '''
    通过酒店名获取所有评论(汇总所有OTA)
    '''
    def get_remarks_by_hotel_name(self, hotel_name):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = '''
                    SELECT remark.* FROM remark,
                    (
                        SELECT baseinfo.* FROM baseinfo,
                        (
                            SELECT * FROM location WHERE hotel_name='%s' AND city = '南京'
                        )temp1
                        WHERE baseinfo.location_id = temp1.guid
                    )temp2
                    WHERE remark.baseinfo_id = temp2.guid
                  '''
            cursor.execute(sql % hotel_name)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data

    def get_remarks_by_text(self, hotel_name, text = None, ota = None):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        result_data = []
        try:
            sql = '''
                    SELECT remark.* FROM remark,
                    (
                        SELECT baseinfo.* FROM baseinfo,
                        (
                            SELECT * FROM location WHERE hotel_name='%s' AND city = '南京'
                        )temp1
                        WHERE baseinfo.location_id = temp1.guid
                    )temp2
                    WHERE remark.baseinfo_id = temp2.guid
                  '''
            if ota is not None:
                sql += " and temp2.OTA = '%s'" % ota
            if text is not None:
                sql += " and remark.remark like '%%" + text + "%%'"
            print sql
            cursor.execute(sql % hotel_name)
            result_data = cursor.fetchall()
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
        return result_data