# -*- coding:utf-8 -*-
__author__ = 'DreamCatcher，LiuYang'

import MySQLdb
import uuid

"""
百度地图API爬取对象-DAO
"""
class BaiduMapDAO(object):
    def __init__(self, host, db, user, password):
        self.host = host
        self.db = db
        self.user = user
        self.password = password

    def setLocalDB(self):
        self.host = 'localhost'
        self.db = 'map'
        self.user = 'root'
        self.password = '1234'

    def setUgcDB(self):
        self.host = "192.168.1.160"
        self.db = "ugcdb"
        self.user = "ugcdb"
        self.password = "ugcdb"

    def setStandarDB(self):
        self.host = "192.168.1.161"
        self.db = "standarddb"
        self.user = "standarddb"
        self.password = "standarddb"


    # 取出周围设施数据
    def get_around_facilities_data(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()
        cursor.execute("SELECT maxdistance FROM around_facilities_distance")
        rows = cursor.fetchall()
        return rows
        db.commit()
        cursor.close()
        db.close()

    # 存储周边设施距离
    def save_around_facilities(self,item):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()

        try:
            print item
            cursor.execute("insert into around_facilities_distance(hotelname,guid,facilities_lntandlang,maxdistance)values(%s,%s,%s,%s)" ,(item["hotelname"],uuid.uuid1(),json.dumps(item["facilities_lntandlang"]),json.dumps(item["maxsite"])))
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()
    # 从数据库中读取周边设施数据
    def _returnarou(self):
        db = MySQLdb.connect(self.host,self.user,self.password,self.db,charset='utf8')
        cursor = db.cursor()

        cursor.execute("SELECT * FROM hotelinfo")
        rows = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
        return rows

    def savePlaceDetail(self, data):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        if 'results' not in data:
            return
        for poi in data['results']:
            try:
                name = poi['name']
                lat = poi['location']['lat']
                lng = poi['location']['lng']
                address = poi['address'] if 'address' in poi else ""
                uid = poi['uid']
                telephone = poi['telephone'] if 'telephone' in poi else ""

                if 'detail_info' in poi:
                    type = poi['detail_info']['type'] if poi['detail_info'].has_key('type') else ""
                    tag = poi['detail_info']['tag'] if poi['detail_info'].has_key('tag') else ""
                    detail_url = poi['detail_info']['detail_url'] if poi['detail_info'].has_key('detail_url') else ""
                    price = poi['detail_info']['price'] if poi['detail_info'].has_key('price') else ""
                    shop_hours = poi['detail_info']['shop_hours'] if poi['detail_info'].has_key('shop_hours') else ""
                    overall_rating = poi['detail_info']['overall_rating'] if poi['detail_info'].has_key(
                            'overall_rating') else ""
                    taste_rating = poi['detail_info']['taste_rating'] if poi['detail_info'].has_key('taste_rating') else ""
                    service_rating = poi['detail_info']['service_rating'] if poi['detail_info'].has_key(
                            'service_rating') else ""
                    environment_rating = poi['detail_info']['environment_rating'] if poi['detail_info'].has_key(
                            'environment_rating') else ""
                    facility_rating = poi['detail_info']['facility_rating'] if poi['detail_info'].has_key(
                            'facility_rating') else ""
                    hygiene_rating = poi['detail_info']['hygiene_rating'] if poi['detail_info'].has_key(
                            'hygiene_rating') else ""
                    technology_rating = poi['detail_info']['technology_rating'] if poi['detail_info'].has_key(
                            'technology_rating') else ""
                    image_num = poi['detail_info']['image_num'] if poi['detail_info'].has_key('image_num') else ""
                    comment_num = poi['detail_info']['comment_num'] if poi['detail_info'].has_key('comment_num') else ""
                    favorite_num = poi['detail_info']['favorite_num'] if poi['detail_info'].has_key('favorite_num') else ""
                    checkin_num = poi['detail_info']['checkin_num'] if poi['detail_info'].has_key('checkin_num') else ""
                    groupon_num = poi['detail_info']['groupon_num'] if poi['detail_info'].has_key('groupon_num') else 0
                    discount_num = poi['detail_info']['discount_num'] if poi['detail_info'].has_key('discount_num') else 0
                else:
                    type = tag = detail_url = price = shop_hours = overall_rating = taste_rating = service_rating = environment_rating = facility_rating = hygiene_rating = technology_rating = image_num = comment_num = favorite_num = checkin_num = ""
                    groupon_num = discount_num = 0
            except:
                print "数据字段获取出错:"+str(poi)
                continue
            try:
                cursor.execute( \
                        "insert into baidupoi(name,lat,lng,address,uid,telephone,type,tag,detail_url,price,shop_hours,overall_rating,taste_rating,service_rating,environment_rating,facility_rating,hygiene_rating,technology_rating,image_num,comment_num,favorite_num,checkin_num,groupon_num,discount_num)\
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (name, lat, lng, address, uid, telephone, type, tag, detail_url, price, shop_hours,
                         overall_rating, taste_rating, service_rating, environment_rating, facility_rating,
                         hygiene_rating, technology_rating, image_num, comment_num, favorite_num, checkin_num,
                         groupon_num, discount_num)
                )
            except Exception, e:
                print e
        db.commit()
        cursor.close()
        db.close()

    def savePlace(self, tableName, data):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        if 'results' not in data:
            return;
        try:
            for poi in data['results']:
                guid = poi['uid']
                name = poi['name']
                address = poi['address']
                x = poi['location']['lng']
                y = poi['location']['lat']
                if 'detail_info' in poi:
                    tag = poi['detail_info']['tag']

                sql = "insert into  " + tableName + " (guid,name,address,type,x,y) values (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE guid = guid"
                cursor.execute(sql, (guid, name, address, tag, x, y))
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()



    # 保存地址节表
    def saveAddressNode(self, tableName, dataList, createBy="baidu_geocoding"):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()

        try:
            for data in dataList:
                sql = "insert into " + tableName + "(guid,地址全称,省,市,区县,街路巷,门牌号,更新人,地理经度,地理纬度,business,direction,distance) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                # TODO 批量插入优化
                addressComponent = data['addressComponent']
                location = data['location']
                distance = addressComponent['distance'] if addressComponent['distance'] != '' else '-1'
                cursor.execute(sql, (
                    uuid.uuid1(), data['formatted_address'], addressComponent['province'],
                    addressComponent['city'], addressComponent['district'], addressComponent['street'], addressComponent['street_number'],
                    createBy,location['lng'], location['lat'],  data['business'], addressComponent['direction'], distance))
        except Exception, e:
            print e

        db.commit()
        cursor.close()
        db.close()

    def saveAddressNodePois(self,tableName, dataList):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            for data in dataList:
                for poi in data["pois"]:
                    guid = poi['uid']
                    name = poi['name']
                    address = poi['addr']
                    x = poi['point']['x']
                    y = poi['point']['y']
                    tag = poi['tag']
                    sql = "insert into  " + tableName + " (guid,name,address,type,x,y) values (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE guid = guid"
                    cursor.execute(sql, (guid, name, address, tag, x, y))
        except Exception, e:
            print e

        db.commit()
        cursor.close()
        db.close()

    def setNullStrToNull(self, tableName):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()
        try:
            sql = "SELECT column_name FROM information_schema.columns WHERE table_name=%s"
            cursor.execute(sql,(tableName))
            data = cursor.fetchall()
            for datum in data:
                cursor.execute("update %s set %s=null where %s=''"%(tableName,datum[0],datum[0]))
                print datum[0]
        except Exception, e:
            print e
        db.commit()
        cursor.close()
        db.close()

    # 清空地址节表
    def truncateAddressNode(self, tableName):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db, charset='utf8')
        cursor = db.cursor()

        try:
            if tableName == 'AddressNode':
                sql = "truncate table " + tableName
                cursor.execute(sql)
        except Exception, e:
            print e

        db.commit()
        cursor.close()
        db.close()

if __name__=="__main__":
    baiduMapDao = BaiduMapDAO()
    baiduMapDao.setNullStrToNull("baidupoi")