# -*- coding:utf-8 -*-
__author__ = 'lizhen'

from weibo import APIClient

class WeiboAPIService(object):

    def __init__(self,appKey="1268278335",appSecret = "204dfdc6e50ea33fe282445f4f0a3b0e",token = "2.005jCfXFLIZp4Bd42d17a3dbC3fmaB"):
        self.appKey = appKey
        self.appSecret = appSecret
        self.token = token
        self.client = APIClient(self.appKey,self.appSecret, redirect_uri='')
        self.client.set_access_token(self.token,0)

    # 获取用户信息
    # 接口详情参考：http://open.weibo.com/wiki/2/users/show
    def getUserInfo(self,screen_name=None,uid=None):
        if screen_name is not None:
            data = self.client.users.show.get(screen_name = screen_name)
        elif uid is not None:
            data = self.client.users.show.get(uid = uid)
        else:
            raise Exception()
        return data

    # 获取某个位置周边的动态
    # 接口详情参考：http://open.weibo.com/wiki/2/place/nearby_timeline
    def getWeibo_nearbyline(self,lat,lon,starttime,endtime,range=3000,count=50,offset=0):
        data = self.client.place.nearby_timeline.get(lat=lat,long=lon,starttime=starttime,endtime=endtime,range=range,count=count,offset=offset)
        return data

    def get_weibo_user_timeline(self, uid, count=50):
        return self.client.place.user_timeline.get(uid=uid, count=count)

    def get_poi_timeline(self, poiid, count=50, page=1):
        return self.client.place.poi_timeline.get(poiid=poiid, count=count, page=page)

    def get_address_to_geo(self, address):
        return self.client.location.geo.address_to_geo.get(address=address)