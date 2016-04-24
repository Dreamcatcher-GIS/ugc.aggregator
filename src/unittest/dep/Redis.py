# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import redis
import json
from service.weibo.WeiboService import WeiboService

weibo_service = WeiboService()

r = redis.Redis(host='localhost',port=6379,db=0)

data = weibo_service.get_all_weibo_nearby_async(32.06852648986326,118.78607144238758,1384876800,1461772800,120)
r.set("foo",json.dumps(data))
print r.get("foo")