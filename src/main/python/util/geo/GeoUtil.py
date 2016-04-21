# -*- coding:utf-8 -*-
import math
from gevent import monkey

from shapely.geometry import Polygon
from shapely.geometry import Point

import gevent
# monkey.patch_all()

import logging

logger = logging.getLogger("ugc")

def frange(x, y, step):
    while x < y:
        yield x
        x += step

'''
地理要素操作Util
'''


class GeoUtil(object):
    '''
    根据bound生成bounds列表,parts=4表示生成4*4的网格
    '''

    def __init__(self):
        # print "Constructor GeoUtil"
        self.pointList = []

    def getBoundsList(self, bounds, parts):
        x1 = bounds[0]
        y1 = bounds[1]
        x2 = bounds[2]
        y2 = bounds[3]
        boundsList = []

        stepX = (x2 - x1) / float(parts)
        stepY = (y2 - y1) / float(parts)
        print str(stepX * parts), (x2 - x1)
        print str(stepY * parts), (y2 - y1)

        print "XStep:%s , YSetp:%s" % (stepX, stepY)

        for startX in frange(x1, x2, stepX):
            print "startX  ", startX
            for startY in frange(y1, y2, stepY):
                # print "startY  ",startY
                endX = startX + stepX
                endY = startY + stepY
                if ((endX < x2) or str(endX) == str(x2)) and ((endY < y2) or str(endY) == str(y2)):
                    print  "var pointx%s=new BMap.Point(%s,%s);" % (1, startX, startY)
                    print  "var pointx%s=new BMap.Point(%s,%s);" % (2, endX, endY)
                    tbounds = [round(startX, 6), round(startY, 6), round(endX, 6), round(endY, 6)]
                    boundsList.append(tbounds)
        boundsSize = len(boundsList)
        print "boundsList-size:", boundsSize
        return boundsList

    # See http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/


    '''
    四分法切割bounds矩形区域
    '''

    def splitBounds(self, bounds,polygon=()):
        x1 = bounds[0]
        y1 = bounds[1]
        x2 = bounds[2]
        y2 = bounds[3]
        # 分割中心点
        splitX = round(((x1 + x2) / 2), 6)
        splitY = round(((y1 + y2) / 2), 6)

        queue = []

        # print  "var pointx%s=new BMap.Point(%s,%s);" % (1, x1, splitY)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (2, splitX, y2)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (3, splitX, splitY)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (4, x2, y2)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (5, x1, y1)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (6, splitX, splitY)
        # print  "var pointx%s=new BMap.Point(%s,%s);" % (7, splitX, y1)
        # print  "var pointx%s=new BMap.Point(%s,%s); \n" % (8, x2, splitY)

        queue.append([x1, y1, splitX, splitY])
        queue.append([x1, splitY, splitX, y2])
        queue.append([splitX, y1, x2, splitY])
        queue.append([splitX, splitY, x2, y2])

        for item in  list(queue):
            coords=self.getPolygonByExtent(item)
            coords=tuple(coords)
            isIntersects=Polygon((coords)).intersects(polygon)
            if isIntersects==False :
                print "remove outside bounds %s " % item
                queue.remove(item)

        return queue



    '''
    将 矩形左上/右下点经纬度转换成闭合矩形点阵
    '''

    def getPolygonByExtent(self, bounds):
        x1 = bounds[0]
        y1 = bounds[1]
        x2 = bounds[2]
        y2 = bounds[3]
        points=[]
        points.append([x1,y1])
        points.append([x1,y2])
        points.append([x2,y2])
        points.append([x2,y1])
        points.append([x1,y1])
        return points

    def getPointByBounds(self, bounds, step, stepParam=0.000011836):

        def frange2(x, y, step):
            while x < y:
                yield x
                x += step
                if x >= y:
                    x = y
                    yield x

        x1 = bounds[0]
        y1 = bounds[1]
        x2 = bounds[2]
        y2 = bounds[3]
        step = round(step * stepParam, 6)
        points = []
        # TODO 大数据量时，需处理内存溢出
        for startY in frange2(y1, y2, step):
            for startX in frange2(x1, x2, step):
                point = str(startY) + ',' + str(startX)
                points.append(point)
        print "range points size : ", len(points)
        return points

    def getPointByBoundsWithFilter(self, polygon, step, stepParam=0.000011836):
        step = round(step * stepParam, 6)
        envelope = polygon.envelope
        srcBounds = envelope.bounds
        boundsList = GeoUtil().getBoundsList(srcBounds, 30)

        threads = []
        results=[]
        processSize = len(boundsList)
        # for i in range(0, processSize, 1):
        #     logger.debug('current process ...%s ' % i)
        #     print 'current process ...%s ' % i
        #     result=threads.append(gevent.spawn(self.getPointByBoundsWithFilterHandler,i,
        #                                polygon, step, boundsList[i]))
        #     results.append(result)
        # gevent.joinall(threads)
        for i in range(0, len(results), 1):
            result=results[i]
            print len(result)
        return results

        # for i in range(0, len(boundsList), 1):
        #     bounds = boundsList[i]
        #     x1 = bounds[0]
        #     y1 = bounds[1]
        #     x2 = bounds[2]
        #     y2 = bounds[3]
        #     points = []
        #     print (y2 - y1) / float(step)
        #     print (x2 - x1) / float(step)
        #     # TODO 大数据量时，需处理内存溢出
        #     for startY in frange2(y1, y2, step):
        #         for startX in frange2(x1, x2, step):
        #             point = str(startY) + ',' + str(startX)
        #             point_wkt = Point(startX, startY)
        #             isIntersects = self.isIntersectsPolygon(polygon, point_wkt)
        #             if isIntersects:
        #                 points.append(point)
        #     print "range points size : ", len(points)
        #     pointsList.append(points)


    def getPointByBoundsWithFilterHandler(self,index, polygon, step, bounds):
        logger.info('current index %s' % index)
        print 'current index %s' % index
        x1 = bounds[0]
        y1 = bounds[1]
        x2 = bounds[2]
        y2 = bounds[3]
        points = []
        print x1,y1  ,    x2,y2
        print (y2 - y1) / float(step)
        print (x2 - x1) / float(step)
        # TODO 大数据量时，需处理内存溢出
        for startY in frange2(y1, y2, step):
            for startX in frange2(x1, x2, step):
                point = str(startY) + ',' + str(startX)
                point_wkt = Point(startX, startY)
                isIntersects = self.isIntersectsPolygon(polygon, point_wkt)
                if isIntersects:
                    points.append(point)
        print "range points size : ", len(points)
        return points

    # geometry是否与polygon相交
    def isIntersectsPolygon(self, polygon, geometry):
        isIntersects = polygon.intersects(geometry)
        return isIntersects
