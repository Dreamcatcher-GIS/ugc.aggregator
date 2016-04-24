# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'


import gevent
import time
import random
from gevent.queue import Queue
import gevent.monkey
gevent.monkey.patch_all()

from service.weibo.APIService import WeiboAPIService
from dao.weibo.WeiboDAO import WeiboDAO
from setting import setting

db_setting = setting["weibo"]


weibo_api_service = WeiboAPIService()
weibo_dao = WeiboDAO(db_setting["host"], db_setting["db"], db_setting["user"], db_setting["password"])

tasks = Queue()
data = Queue()

id_str = "2089426035,3184474850,2791587541,2387367447,3753741655,2868119530,5668346330,1783003347,5048084657"
id_list = id_str.split(",")
for id in id_list:
    tasks.put_nowait(id)
time1 = time.time()
api_accounts = weibo_dao.get_weibo_accounts()

def request(x):
    while not tasks.empty():
        random_num = random.randrange(0, len(api_accounts))
        api_account = api_accounts[random_num]
        client = WeiboAPIService(appKey=api_account[1], appSecret=api_account[2], token=api_account[3])
        id = tasks.get_nowait()
        print u"线程%d:\nid:%s"%(x,id)
        data.put_nowait(client.get_weibo_user_timeline(id))

gevent.joinall([
    gevent.spawn(request,1),
    gevent.spawn(request,2),
    gevent.spawn(request,3),
    gevent.spawn(request,4),
    gevent.spawn(request,5),
    gevent.spawn(request,6),
    gevent.spawn(request,7),
    gevent.spawn(request,8),
    gevent.spawn(request,9)
])
time2 = time.time()

print time2-time1