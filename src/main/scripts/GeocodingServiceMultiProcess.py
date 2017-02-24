#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util.geo.GeoUtil import GeoUtil

__author__ = 'geosmart'
import copy_reg
import multiprocessing
import types
from multiprocessing import Pool
from time import  time

from service.map.baidu.SnatcherService import BaiduMapSnatcherService
from util.common.CollectionUtil import CollectionUtil


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)


copy_reg.pickle(types.MethodType, _pickle_method)
# "bmm9EcjvS4TnnRzoZoYXXcAF",
akList = ["fkw1bmMoGBGWOAGmpqIWxahy", "lWpbR5OCQYybppqci2kGYgFd", "DW2CwL3B3271CiVyw7GdBsfR",
          "ou5X9BBEMZtwvuSO4Ypfx2HB", "LPtK0OiWUItxFK6qd3m1FsRD","K1bHzgxG2osaIiKyAAel57jQ",
          "dRtL7RRo4YTdtujclWx85DtG", "G4UkrVktXE71zQsGY8Vza3Ih", "cmrsVXBcAlvhbFeaRwCsGUnH", "WBw4kIepZzGp4kH5Gn3r0ACy",
          ]
class GeocodingService(object):
    def __init__(self):
        print "Constructor ... %s" % multiprocessing.current_process().name

    def __del__(self):
        print "... Destructor %s" % multiprocessing.current_process().name

    def fetchAddressNodeByPoints(self, index, points):
        print 'current index %s,points %s' % (index, str(len(points)))
        snatcherService = BaiduMapSnatcherService(akList[0])
        snatcherService.fetchAddressNode(points)
        print 'Process %s done' % index
        # TODO multiprocessing多进程实现，此处代码最后一个process不执行fetchAddressNode内的代码

    # multiprocessing多进程并发
    def run(self):
        bounds = [113.149662, 23.038528, 113.15175, 23.039123]
        # bounds = [113.129391, 22.98257, 113.261335, 23.072904]
        step = 1
        snatcherService = BaiduMapSnatcherService()
        # 获取区域内点集
        points = GeoUtil().getPointByBounds(bounds, step)
        regionSize = len(points) / len(akList)
        # 点集合子集
        subPoints = CollectionUtil().chunksBySize(points, regionSize)

        processSize = len(subPoints)
        pool = Pool(processes=processSize)
        results = []
        print 'process size  %s ,per process data sizes %s' % (processSize, regionSize)
        for index in range(0, processSize, 1):
            print 'current process  %s ' % index
            r = pool.apply_async(self.fetchAddressNodeByPoints, args=(index, subPoints[index]))
            results.append(r)

        for r in results:
            r.wait()
            print 'successful'

if __name__ == '__main__':
    # python E:\PythonWorkspace\sta\UGC_Agrregator\service\map\map\GeocodingService.py
    ts = time()
    service = GeocodingService()
    # service.asynchronous()
    service.run()
    print 'Took %s' % format(time() - ts)
    raw_input()
