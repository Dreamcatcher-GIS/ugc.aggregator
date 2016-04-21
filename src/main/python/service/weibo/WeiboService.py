# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import random
import datetime

from service.weibo.APIService import WeiboAPIService
from service.map.baidu.APIService import BaiduMapAPIService
from dao.weibo.WeiboDAO import WeiboDAO
from setting import setting

db_setting = setting["weibo"]

class WeiboService(object):

    def __init__(self):
        self.weiboDAO = WeiboDAO(db_setting["host"], db_setting["db"], db_setting["user"], db_setting["password"])
        self.apiService = WeiboAPIService()
        self.api_accounts = None

    def random_api_account(self):
        if self.api_accounts == None:
            self.api_accounts = self.weiboDAO.get_weibo_accounts()
        # 随机数
        random_num = random.randrange(0, len(self.api_accounts))
        api_account = self.api_accounts[random_num]
        self.apiService = WeiboAPIService(appKey=api_account[1], appSecret=api_account[2], token=api_account[3])

    '''
    获取该地点和时间内所有的签到微博
    '''
    def get_all_weibo_nearby(self, lat, lng, starttime, endtime, range=3000, count=50, offset=0):
        weibo_data = []
        query_queue = [[starttime, endtime]]
        while len(query_queue) != 0:
            time_range = query_queue.pop()
            try:
                # 随机取出微博开放平台秘钥
                self.random_api_account()
                data = self.apiService.getWeibo_nearbyline(lat, lng, time_range[0], time_range[1], range, count, offset)
            except Exception, e:
                print e
                query_queue.append(time_range)
                continue
            if "statuses" in data:
                if len(data['statuses']) >= 49:
                    mid_time = int((time_range[1]+time_range[0])/2)
                    query_queue.append([time_range[0],mid_time])
                    query_queue.append([mid_time,time_range[1]])
                else:
                    weibo_data.extend(data['statuses'])
        return weibo_data

    '''
    根据年份对微博数据进行统计
    '''
    def nearby_weibo_statis_wrapper(self, data):
        # 百度地图api服务
        self.baidu_api_service = BaiduMapAPIService("MviPFAcx5I6f1FkRQlq6iTxc")
        # 统计数据
        statis_item = {}
        # 存放来源城市的地理位置
        statis_item["city_location"] = {}
        # 统计签到博主的来源
        statis_item["city_counter"] = {}
        for datum in data:
            if "created_at" in datum:
                # 获取微博创建时间
                t = datetime.datetime.strptime(datum["created_at"],"%a %b %d %H:%M:%S +0800 %Y")
                year = t.strftime("%Y")
                location = datum["user"]["location"]
                if location == u"其他":
                    continue
                # 来源地统计
                if location not in statis_item["city_location"]:
                    # 从数据表中取出地址
                    location_info = self.weiboDAO.get_location(location)
                    # 如果数据表中没有,则调用百度地图api地理编码,并保存到数据库中
                    if location_info == None:
                        geocoding_info = self.baidu_api_service.doGeocoding(location)
                        geocoding_info = {"city":location, "x":geocoding_info["result"]["location"]["lng"], "y":geocoding_info["result"]["location"]["lat"]}

                        self.weiboDAO.save_location(geocoding_info)
                        statis_item["city_location"][location] = {"x":geocoding_info["x"], "y":geocoding_info["y"]}
                    else:
                        statis_item["city_location"][location] = {"x":location_info[1], "y":location_info[2]}
                # 根据年份进行聚合统计
                if year in statis_item["city_counter"]:
                    # 获取来源地的地理坐标
                    if location in statis_item["city_counter"][year]:
                        statis_item["city_counter"][year][location] += 1
                    else:
                        statis_item["city_counter"][year][location] = 1
                else:
                    statis_item["city_counter"][year] = {}
                    statis_item["city_counter"][year][location] = 1
        return statis_item

    '''
    获取一组用户的签到时间线
    '''
    def get_weibo_users_timeline(self, usersid):
        result_data = {}
        userid_list = usersid.split(',')
        for userid in userid_list:
            user_timeline = self.apiService.get_weibo_user_timeline(userid)
            result_data[userid] = user_timeline
        return result_data

    def saveWeibo_byCycle(self,lat,lon,starttime,endtime,radius=3000,count=50,offset=0):
        data = self.apiService.getWeibo_nearbyline(lat=lat, lon=lon,starttime=starttime,endtime=endtime,range=radius,count=count,offset=offset)
        weibonumber = len(data["statuses"])
        for i in range(0,weibonumber):
            # 取微博ID
            weiboid=data["statuses"][i]["id"].encode('utf-8')
            #取text
            try:
                if text.startswith('http'):
                    text=''
                else:
                    text = data["statuses"][i]["text"].encode('utf-8')
            except:
                text = "unknown"
            #取经纬度
            # try:
            if "annotations" in data["statuses"][i]:
                if "place" in data["statuses"][i]["annotations"]:
                    lat = data["statuses"][i]["annotations"]["place"]["lat"]
                    lon = data["statuses"][i]["annotations"]["place"]["lon"]
                else:
                    lat=data["statuses"][i]["geo"]["coordinates"][0]
                    lon=data["statuses"][i]["geo"]["coordinates"][1]
            else:
                lat=data["statuses"][i]["geo"]["coordinates"][0]
                lon=data["statuses"][i]["geo"]["coordinates"][1]

            #取title
            if "annotations" in data["statuses"][i]:
                if "title" in data["statuses"][i]["annotations"]:
                    title = data["statuses"][i]["annotations"]["place"]["title"]
                else:
                    title='unknow'.encode('utf-8')
            else:
                title='unknow'.encode('utf-8')

            # 取userid
            userid=data["statuses"][i]["user"]["id"].encode('utf-8')
            #取location
            location = data["statuses"][i]["user"]["location"]
            #取userdescription
            decription = data["statuses"][i]["user"]["description"].encode('utf-8')
            #取gender

            gender = data["statuses"][i]["user"]["gender"]

            #取时间
            created_at=data["statuses"][i]["user"]["created_at"]
            monthdict = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
            timelist = created_at.split()
            timestrnew = '%s-%s-%s %s' %(timelist[-1] ,monthdict[timelist[1]], timelist[2] ,timelist[3])
            timestrnew = timestrnew.encode('utf-8')
            #取地点类型
            try:
                if "object" in data["statuses"][i]["url_objects"][i]:
                    if "object" in data["statuses"][i]["url_objects"][i]["object"]:
                        if "address" in data["statuses"][i]["url_objects"][i]["object"]["object"]:
                            if "fax" in data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]:
                                fax = data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]["fax"]
                else:
                    fax='unknow'.encode('utf-8')
            except IndexError:
                fax='unknow'.encode('utf-8')
            #取城市名
            try:
                if "object" in data["statuses"][i]["url_objects"][i]:
                    if "object" in data["statuses"][i]["url_objects"][i]["object"]:
                        if "address" in data["statuses"][i]["url_objects"][i]["object"]["object"]:
                            if "locality" in data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]:
                                locality = data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]["locality"]
                else:
                    locality='unknow'
            except IndexError:
                locality='unknow'.encode('utf-8')

            #取街道名
            try:
                if "object" in data["statuses"][i]["url_objects"][i]:
                    if "object" in data["statuses"][i]["url_objects"][i]["object"]:
                        if "address" in data["statuses"][i]["url_objects"][i]["object"]["object"]:
                            if "formatted" in data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]:
                                formatted = data["statuses"][i]["url_objects"][i]["object"]["object"]["address"]["formatted"]
                else:
                    formatted='unknow'.encode('utf-8')
            except IndexError:
                formatted='unknow'.encode('utf-8')

            #写入mysql,因特殊字符写入问题，将text和description中含有特殊字符按unknown处理
            try:
                self.weiboDAO.saveWeibo_ByAPI(weiboid,text,lat,lon,title,userid,location,decription,gender,timestrnew,fax,locality,formatted)
            except Exception:
                decription="unknown"
                text = "unknown"
                self.weiboDAO.saveWeibo_ByAPI(weiboid,text,lat,lon,title,userid,location,decription,gender,timestrnew,fax,locality,formatted)
