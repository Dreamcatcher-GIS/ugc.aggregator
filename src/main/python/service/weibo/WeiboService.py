# -*- coding:utf-8 -*-
import json
import traceback

__author__ = 'lizhen'

import random
import datetime
import gevent
import gevent.monkey
from gevent.queue import Queue
gevent.monkey.patch_all()

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
                    mid_time = int((int(time_range[1])+int(time_range[0]))/2)
                    query_queue.append([time_range[0],mid_time])
                    query_queue.append([mid_time,time_range[1]])
                else:
                    weibo_data.extend(data['statuses'])
        return weibo_data

    '''
    异步获取该地点和时间内所有的签到微博
    '''
    def get_all_weibo_nearby_async(self, lat, lng, starttime, endtime, radius=3000, count=50, offset=0):
        def weibo_nearby(api_account):
            client = WeiboAPIService(appKey=api_account[1], appSecret=api_account[2], token=api_account[3])
            while not tasks.empty():
                time_range = tasks.get_nowait()
                try:
                    print "thread start:  account:"+str(api_account)+"  range:"+str(time_range)
                    info = client.getWeibo_nearbyline(lat,lng,time_range[0],time_range[1],radius,count,offset)
                    if "statuses" in info:
                        if len(info['statuses']) >= 49:
                            mid_time = int((int(time_range[1])+int(time_range[0]))/2)
                            tasks.put_nowait([time_range[0],mid_time])
                            tasks.put_nowait([mid_time,time_range[1]])
                        else:
                            data.put_nowait(info['statuses'])
                    print "thread end:  account:"+str(api_account)+"  range:"+str(time_range)
                except:
                    traceback.print_exc()
                    tasks.put_nowait(time_range)
                    continue

        # 结果数据
        result_data = []
        # 线程存储数据
        data = Queue()
        # 任务
        tasks = Queue()
        # 查看可用的api账号
        if self.api_accounts == None:
            self.api_accounts = self.weiboDAO.get_weibo_accounts()
        step = int((endtime-starttime)/len(self.api_accounts)/int(radius/100))
        # 切割查询时间区域至task中
        for i in range(0,len(self.api_accounts)*int(radius/100)-1):
            tasks.put_nowait([starttime+step*i,starttime+step*(i+1)])
        # 根据微博api账号数执行线程
        threads = []
        for account in self.api_accounts:
            threads.append(gevent.spawn(weibo_nearby,account))
        gevent.joinall(threads)
        while not data.empty():
            result_data.extend(data.get_nowait())
        return result_data

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
        # 微博内容
        statis_item["weibo_info"] = data
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
    同步获取一组用户的签到微博
    '''
    def get_weibo_users_timeline(self, id_str):
        result_data = {}
        userid_list = id_str.split(',')
        for userid in userid_list:
            self.random_api_account()
            user_timeline = self.apiService.get_weibo_user_timeline(userid,count=20)
            result_data[userid] = user_timeline
        return result_data


    '''
    异步获取一组用户的签到微博
    '''
    def get_weibo_users_timeline_async(self, id_str):
        def get_timeline_data(api_account):
            while not tasks.empty():
                client = WeiboAPIService(appKey=api_account[1], appSecret=api_account[2], token=api_account[3])
                id = tasks.get_nowait()
                data.put_nowait(client.get_weibo_user_timeline(id))
        result_data = []
        data = Queue()
        tasks = Queue()

        for id in id_str.split(",")[0:10]:
            tasks.put_nowait(id)
        # 查看可用的api账号
        if self.api_accounts == None:
            self.api_accounts = self.weiboDAO.get_weibo_accounts()
        threads = []
        for account in self.api_accounts:
            threads.append(gevent.spawn(get_timeline_data,account))
        gevent.joinall(threads)
        while not data.empty():
            result_data.append(data.get_nowait())
        return result_data


    def get_weibo_users_timeline_statics(self, id_str):
        result_data = {}
        result_data["line"] = []
        result_data["point"] = {}
        weibo_data = self.get_weibo_users_timeline_async(id_str)
        for item in weibo_data:
            line = item["statuses"]
            for i in range(0, len(line)-1):
                try:
                    start_place = line[i]["annotations"][0]["place"]
                    end_place = line[i+1]["annotations"][0]["place"]
                    if start_place["lat"] != end_place["lat"]:
                        start_point = {"name":start_place["title"],"geoCoord":[start_place["lon"],start_place["lat"]]}
                        end_point = {"name":end_place["title"],"geoCoord":[end_place["lon"],end_place["lat"]],"value":1}
                        result_data["line"].append([start_point,end_point])
                    coord_str = str(end_place["lon"])+","+str(end_place["lat"])
                    if coord_str not in result_data["point"]:
                        result_data["point"][coord_str] = {
                            "name":end_place["title"],
                            "geoCoord":[
                                end_place["lon"],
                                end_place["lat"]
                            ],
                            "value":1
                        }
                    else:
                        result_data["point"][coord_str]["value"]+=1
                except:
                    continue
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
