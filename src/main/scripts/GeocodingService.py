#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from time import time, strftime, localtime
import os
import shutil

from util.geo.GeoUtil import GeoUtil
from util.common.CollectionUtil import CollectionUtil
from util.io.FileUtil import FileUtil

import gevent
import gevent.monkey

gevent.monkey.patch_socket()

import logging
import logging.config
from setting import baidu_map_uadb_setting

logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger("ugc")

from service.map.baidu.SnatcherService import BaiduMapSnatcherService

# 数据库配置
dao_setting = baidu_map_uadb_setting

def frange2(x, y, step):
    while x < y:
        yield x
        x += step
        if x >= y:
            x = y
            yield x


# 每个Token正向编码100万，企业号300万
goodAkList = ["lWpbR5OCQYybppqci2kGYgFd", "WBw4kIepZzGp4kH5Gn3r0ACy", "ou5X9BBEMZtwvuSO4Ypfx2HB",
              "Qdgt7mclCrkFdPBizd3uUWsE","lWhyznAxPPYdanHLKZpjR272","e5UujacxFn50xo2RadnTEtly",
              "WEC1LKpjIWfCehFqGVPm6Dn6", "DW2CwL3B3271CiVyw7GdBsfR", "LPtK0OiWUItxFK6qd3m1FsRD",
              "oD8Okbi8FdRm5keKBvfHuR7H","K1bHzgxG2osaIiKyAAel57jQ",
              "MviPFAcx5I6f1FkRQlq6iTxc", "MviPFAcx5I6f1FkRQlq6iTxc","MviPFAcx5I6f1FkRQlq6iTxc",
              "B3Z9TG0QdQ5omGKLnPqEm3OWeMbogln8","GOnUNZzHBUlVsSbuZIfr8XCCqLRonKjM"
             ]

path = "c:/data/point_cache/"
path_bak = "c:/data/point_cache_bak/" + strftime("%Y-%m-%d %H-%M-%S", localtime(time()))
if os.path.exists(path_bak) == False:
    os.makedirs(path_bak)


# 调用百度GeocodingAPI爬取数据
class GeocodingService(object):

    # 地址节表名
    addressNodeTableName = 'AddressNode_Xuzhou'
    # poi点表名
    placeTableName = 'Place_Xuzhou'

    def fetchAddressNodeByPoints(self, index, points):
        # 循环Token，
        if index >= len(goodAkList):
            token = goodAkList[-1]
        else:
            token = goodAkList[index]

        logger.info('current index %s,points %s' % (index, str(len(points))))
        snatcherService = BaiduMapSnatcherService(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"], token)
        snatcherService.fetchAddressNode(index, points, self.addressNodeTableName,placeTableName=self.placeTableName)
        logger.debug('Process %s done' % index)
        # TODO multiprocessing多进程实现，此处代码最后一个process不执行fetchAddressNode内的代码

    def run(self):
        pointList = []
        limitSize = 950000
        # TODO 从文件缓存读取limitSize个points，待测试
        fileNames = os.listdir(path)
        # 从point_cache读取大约limitSize*len(goodAkList)个点，并将读取的文件移至point_cache_bak文件夹
        for fileName in fileNames:
            print len(pointList)
            if len(pointList) < (limitSize) * len(goodAkList):
                file = path + fileName
                myList = FileUtil().readFileToObj(file)
                logger.debug("read file %s,size %s" % (file, len(myList)))
                pointList.extend(myList)

                print  "cut file %s to %s" % (file, path_bak)
                shutil.move(file, path_bak + "")
            else:
                break
        # 将所有点按goodAkList的数目分桶装载
        chunkPoints = CollectionUtil().chunksByAverage(pointList,len(goodAkList))
        threads = []
        threadSize = len(chunkPoints)
        logger.debug('thread size ...%s ' % threadSize)
        # 6个线程分发桶中的点数据
        for i in xrange(0, threadSize, 1):
            threadChunkPointsList = CollectionUtil().chunksBySize(chunkPoints[i], limitSize / 6)
            for j in xrange(0, len(threadChunkPointsList), 1):
                index = str(i) + "_" + str(j)
                logger.debug('current thread ...%s ' % index)
                threads.append(gevent.spawn(self.fetchAddressNodeByPoints, i, threadChunkPointsList[j]))
        gevent.joinall(threads)
        # 将地址节表中的空字符串设置为null
        snatcherService = BaiduMapSnatcherService(dao_setting["host"], dao_setting["db"], dao_setting["user"], dao_setting["password"])
        snatcherService.setNullStrToNull(self.addressNodeTableName)

    def concurrentRequest(self):
        # 测试
        # bounds = [113.149662, 23.038528, 113.15175, 23.039123]
        # 桂城街道
        bounds = [113.129391, 22.98257, 113.261335, 23.072904]
        # 狮山镇
        # bounds = [113.092391, 23.132011, 113.123293, 23.167699]
        # 南京
        # bounds = [118.710042, 31.960759, 118.905082, 32.134843]
        # 获取区域内点集
        points = GeoUtil().getPointByBounds(bounds, 1000)
        start = int(math.ceil(len(points) / 2))
        # 点集拆分爬取
        # end = len(points)
        # points = points[start:end]
        points = points[0:start]

        logger.debug('points size %s' % len(points))
        # 点集合子集
        subPoints = CollectionUtil().chunksByAverage(points, len(goodAkList))

        threads = []
        processSize = len(subPoints)
        logger.debug('process size ...%s ,per process data size...%s' % (processSize, len(subPoints)))
        for index in range(0, processSize, 1):
            logger.debug('current process ...%s ' % index)
            threads.append(gevent.spawn(self.fetchAddressNodeByPoints, index, subPoints[index]))
        gevent.joinall(threads)


if __name__ == '__main__':
    # python E:\PythonWorkspace\ugc\ugc.aggregator\src\main\scripts\GeocodingService.py
    ts = time()
    service = GeocodingService()
    # service.concurrentRequest()
    service.run()

    logger.debug('Took %s' % format(time() - ts))
