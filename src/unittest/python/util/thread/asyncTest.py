#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy_reg
import multiprocessing
import types
from multiprocessing import Pool

from service.map.baidu.SnatcherService import BaiduMapSnatcherService


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)
akList=["DW2CwL3B3271CiVyw7GdBsfR","fkw1bmMoGBGWOAGmpqIWxahy","tPWoYd2a64Gc84Gc7ywP6bqK","xxOTUAdTdOXERG9TMsab5fme",
        "gifHg8SStstrIlI1Gm1qi2Gp","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","fkw1bmMoGBGWOAGmpqIWxahy",
        "DW2CwL3B3271CiVyw7GdBsfR","fkw1bmMoGBGWOAGmpqIWxahy","tPWoYd2a64Gc84Gc7ywP6bqK","xxOTUAdTdOXERG9TMsab5fme",
        "bmm9EcjvS4TnnRzoZoYXXcAF","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","xxOTUAdTdOXERG9TMsab5fme",
        "gifHg8SStstrIlI1Gm1qi2Gp","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","xxOTUAdTdOXERG9TMsab5fme",
        "bmm9EcjvS4TnnRzoZoYXXcAF","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","xxOTUAdTdOXERG9TMsab5fme",
        "fkw1bmMoGBGWOAGmpqIWxahy","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","fkw1bmMoGBGWOAGmpqIWxahy",
        "bmm9EcjvS4TnnRzoZoYXXcAF","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","fkw1bmMoGBGWOAGmpqIWxahy",
        "gifHg8SStstrIlI1Gm1qi2Gp","Ug13ut1UsnMV6NYiDznZFuDk","X40vyGYCMUEBXUZIEjH0qFpa","fkw1bmMoGBGWOAGmpqIWxahy"]

class Klass(object):
    def __init__(self):
        print "Constructor ... %s" % multiprocessing.current_process().name

    def __del__(self):
        print "... Destructor %s" % multiprocessing.current_process().name

    def func(self, x):
        print(x * x)

    def fetchAddressNodeByBoundsList(self,bounds):
            print 'fetchAddressNodeByBoundsList---%s ' % bounds
            x1=bounds[0]
            y1=bounds[1]
            x2=bounds[2]
            y2=bounds[3]
            akIndex=bounds[4]
            print 'ak---%s ' % akList[akIndex]
            snatcherService = BaiduMapSnatcherService(akList[akIndex])
            snatcherService.fetchAddressNode(x1,y1,x2,y2);

    def run(self):
        bounds=[113.129391,22.98257,113.261335,23.072904]
        step=0.125
        snatcherService = BaiduMapSnatcherService()
        boundsList=snatcherService.getBoundsList(bounds,step)

        pool = Pool(processes=len(boundsList))

        results = []
        for index in range(0, len(boundsList),1):
            bounds=boundsList[index]
            bounds.append(index);
            r = pool.apply_async(self.fetchAddressNodeByBoundsList,args = (bounds, ))
            results.append(r)

        for r in results:
            r.wait()
            print 'successful'

if __name__ == '__main__':
    _kls = Klass()
    _kls.run()