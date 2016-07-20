# -*- coding:utf-8 -*-

from service.map.baidu.APIService import BaiduMapAPIService
from dao.map.BaiduMapDAO import BaiduMapDAO

import multiprocessing

import logging
import re
from math import *
import json

from util.geo.GeoUtil import GeoUtil

logger = logging.getLogger("ugc")


def frange(x, y, step):
    while x < y:
        yield x
        x += step


class BaiduMapSnatcherService(object):
    def __init__(self, host, db, user, password, ak="DW2CwL3B3271CiVyw7GdBsfR"):
        logging.debug("Constructor  ak:%s" % ak)
        self.baiduAPIService = BaiduMapAPIService(ak)
        self.baiduMapDAO = BaiduMapDAO(host, db, user, password)
        self.around_facilities_distance = [] # 存放最后要存入数据库的周边设施列表
        self.around_data = {} # 存放最后存入数据库的全部信息列表
        self.around_facilities_zuobiao = [] # 酒店坐标列表
        self.around_facilities_zhoubiansheshibiaozuoliebiao = [] # 周边设施坐标列表
        self.facilities_ditance = [] # 存储设施名字对应与酒店间距离的列表
        self.maxdistance_and_hotelzuobiao = [] # 存放最远距离设置和坐标
        self.hotelname_and_zuobiao = []  #存放酒店的名字和坐标
        self.disigeziduan = [] #最后存入数据库的第四个字段
        self.bed = {}

    # def __del__(self):
    #     print "... Destructor BaiduMapSnatcherService...  %s" % multiprocessing.current_process().name

    '''
    取出设施距离数据
    '''
    def Get_around_facilities_data(self):
        data = self.baiduMapDAO.get_around_facilities_data()
        b = 0  #距离在100以下
        c = 0  #距离在100到200
        d = 0  #距离在200到300
        e = 0  #距离在300到400
        f = 0  #距离在400到500
        g = 0  #距离在500到600
        h = 0  #距离在600到700
        I = 0  #距离在700到800
        J = 0  #距离在800到900
        K = 0  #距离在900到1000
        L = 0  #距离在1000以上
        for i in data:
            a = json.loads(i[0])
            if a[1][1] <100:
                b = b+1
            elif a[1][1] >= 100 and a[1][1] < 200:
                c = c+1
            elif a[1][1] >= 200 and a[1][1] <300:
                d = d+1
            elif a[1][1] >= 300 and a[1][1] < 400:
                e = e + 1
            elif a[1][1] >= 400 and a[1][1] < 500:
                f = f + 1
            elif a[1][1] >= 500 and a[1][1] < 600:
                g = g + 1
            elif a[1][1] >= 600 and a[1][1] < 700:
                h = h + 1
            elif a[1][1] >= 700 and a[1][1] < 800:
                I = I + 1
            elif a[1][1] >= 800 and a[1][1] < 900:
                J = J + 1
            elif a[1][1] >= 900 and a[1][1] < 1000:
                K = K + 1
            elif a[1][1] >= 1000:
                L = L + 1
        print str(b) + " " + str(c) + " " + str(d) + " " + str(e) + " " + str(f) + " " + str(g) + " " + str(h) + " " + str(I) + " " + str(J) + " " + str(K) + " " + str(L)


    '''
    从数据库读取周边设施数据
    '''
    def getdata(self):

        Data = self.baiduMapDAO._returnarou()
        for data in Data:
            if len(data[-1]):
                try:
                    self.manage_around_falities(data[-1],data[2])
                    self.around_data["hotelname"] = data[2]
                    self.around_data["facilities_lntandlang"] = self.around_facilities_distance
                    self.get_maxdistance_facilities()
                    # self.baiduMapDAO.save_around_facilities(self.around_data)
                    self.facilities_ditance = []
                    self.disigeziduan = []
                    self.maxdistance_and_hotelzuobiao = []
                    self.around_facilities_zuobiao = []
                    self.hotelname_and_zuobiao = []
                    self.around_facilities_distance = []
                    self.around_facilities_zhoubiansheshibiaozuoliebiao = []
                    self.around_data = {}
                except:
                    pass

    '''
    南京市纬度范围31°14″至32°37″
    南京市经度范围东经118°22″至119°14″
    '''
    def manage_around_falities(self,data,hoteldata):
        if len(data):
            data1 = re.sub(':',',',data)
            data2 = re.sub(';',',',data1)
            data3 = re.sub(',,',',',data2)
            data4 = data3.split(",")
            hotel_coordinate_data = self.baiduAPIService.doGeocoding(hoteldata,u"南京市")
            hotel_coordinate_x = hotel_coordinate_data["result"]["location"]["lng"]
            hotel_coordinate_y = hotel_coordinate_data["result"]["location"]["lat"]

            self.around_facilities_zuobiao.append(hotel_coordinate_x)
            self.around_facilities_zuobiao.append(hotel_coordinate_y)

            self.hotelname_and_zuobiao.append(hoteldata)
            self.hotelname_and_zuobiao.append(self.around_facilities_zuobiao)

            self.around_facilities_distance.append(self.around_facilities_zuobiao)
            # i 是传入的地址名
            for i in range(len(data4)):
                self.getjingweifu(data4[i],hotel_coordinate_x,hotel_coordinate_y)
            self.around_facilities_distance.append(self.around_facilities_zhoubiansheshibiaozuoliebiao)


    '''
    传入地址名获得经纬度信息
    '''
    def getjingweifu(self,facilities_data,hotel_coordinate_x,hotel_coordinate_y):
        try:
            data = self.baiduAPIService.doGeocoding(facilities_data,u"南京市")
            if data['result']['location']["lng"] >= 118:
                if data['result']['location']["lng"] <= 119.5:
                    if data['result']['location']["lat"] >=30.5:
                        if data['result']['location']["lat"] <=32.8:
                            if len(self.around_facilities_zhoubiansheshibiaozuoliebiao) < 3:
                                self.around_facilities_zhoubiansheshibiaozuoliebiao.append([data['result']['location']["lng"],data['result']['location']["lat"]])
                                self.compute(hotel_coordinate_x,hotel_coordinate_y,data['result']['location']["lng"],data['result']['location']["lat"],facilities_data)
        except:
            pass

    '''
    计算酒店和设施点的距离
    '''
    def compute(self,hotel_x,hotel_y,facilities_x,facilities_y,facilities_name):
        distance = 6371 * math.acos(math.cos(hotel_y)*math.cos(facilities_y)*math.cos(hotel_x-facilities_x)+math.sin(hotel_y)*math.sin(facilities_y))
        print distance
        self.facilities_ditance.append({facilities_name:distance})

    '''
    找出最远距离的设施点
    '''
    def get_maxdistance_facilities(self):
        min = self.facilities_ditance[0].values()
        for i in self.facilities_ditance:
            if i.values()[0] < min:
                min = i.values()[0]

        max = min

        for i in self.facilities_ditance:
            if i.values()[0] > max:
                if i.values()[0] < 1500:
                    max = i.values()[0]

        for i in self.facilities_ditance:
            for q,w in i.items():
                if w == max:
                    self.maxdistance_and_hotelzuobiao.append(q)
                    self.maxdistance_and_hotelzuobiao.append(w)
                    self.disigeziduan.append(self.hotelname_and_zuobiao)
                    self.disigeziduan.append(self.maxdistance_and_hotelzuobiao)
                    self.disigeziduan
                    self.around_data["maxsite"] = self.disigeziduan
                    break

    '''
    计算地球上两点的距离
    '''
    def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):
         ra = 6378.140  # 赤道半径 (km)
         rb = 6356.755  # 极半径 (km)
         flatten = (ra - rb) / ra  # 地球扁率
         rad_lat_A = radians(Lat_A)
         rad_lng_A = radians(Lng_A)
         rad_lat_B = radians(Lat_B)
         rad_lng_B = radians(Lng_B)
         pA = atan(rb / ra * tan(rad_lat_A))
         pB = atan(rb / ra * tan(rad_lat_B))
         xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
         c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
         c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
         dr = flatten / 8 * (c1 - c2)
         distance = ra * (xx + dr)
         return distance



    # 抓取Place详情
    def fetchPlaceDetail(self, lng0, lat0, lng1, lat1, query):
        # 使用矩形范围初始栈
        queue = [[lng0, lat0, lng1, lat1]]
        # 用以存放返回值为0的矩形范围
        zero_queue = []
        while len(queue) != 0:
            # 取出一个查询范围
            range = queue.pop()
            # 根据范围进行查询
            try:
                data = self.baiduAPIService.placeSearch(query=query,
                                                    bounds="%lf,%lf,%lf,%lf" % (range[1], range[0], range[3], range[2]))
            except Exception, e:
                print e
                print u"查询数据出错"
                queue.append(range)
                continue
            # 查看数据是否有效
            try:
                print u"范围查询就结果个数： " + str(len(data['results']))
            except:
                print u"查询数据返回内容出错"
                continue
            if data.has_key('results'):
                # 如果范围的poi等于20,就切割该范围,并将切割后的子范围置入栈中
                if len(data['results']) == 20:
                    splitX = (range[0] + range[2]) / 2
                    splitY = (range[1] + range[3]) / 2
                    if (range[2] - range[0]) < 0.001 or (range[3] - range[1]) < 0.001:
                        continue
                    queue.append([range[0], splitY, splitX, range[3]])
                    queue.append([splitX, splitY, range[2], range[3]])
                    queue.append([range[0], range[1], splitX, splitY])
                    queue.append([splitX, range[1], range[2], splitY])
                    continue
                elif len(data['results']) == 0:
                    zero_queue.append(range)
                # 如果查询结果小于20则存储
                else:
                    self.baiduMapDAO.savePlaceDetail(data)
        return zero_queue

    '''
    根据extend范围调用Place API抓取POI
    '''

    def fetchPlacePagination(self, lng0, lat0, lng1, lat1, keyWords, tableName="Place_nanjing"):
        # 使用矩形范围初始栈
        queue = [[lng0, lat0, lng1, lat1]]
        bounds = queue.pop()
        data = self.baiduAPIService.placeSearchBatch(keyWords,
                                                     "%lf,%lf,%lf,%lf" % (bounds[1], bounds[0], bounds[3], bounds[2]))
        self.baiduMapDAO.savePlace(tableName, data)

        total = data["total"]
        totalPages = self.getDataTotalPage(total)
        logger.info("total:%s , totalPages: %s" % (total, totalPages))

        for pageNumber in range(1, totalPages, 1):
            data = self.baiduAPIService.placeSearchBatch(keyWords, bounds, pageNumber)
            self.baiduMapDAO.savePlace(tableName, data)

    def getDataTotalPage(self, total, pageSize=20):
        totalPages = 0
        if (total == 0):
            totalPages = 0
        else:
            if (total % pageSize > 0):
                totalPages = (int)(total / pageSize + 1)
            else:
                totalPages = (int)(total / pageSize)
        return totalPages

    def fetchPlace(self, polygon, lng0, lat0, lng1, lat1, keyWords, step=1, stepParam=0.000011836, tableName="Place"):
        '''
        根据extend范围调用Place API抓取POI
        '''

        # 使用矩形范围初始栈
        boundsQueue = [[lng0, lat0, lng1, lat1]]
        step = round(step * stepParam, 6)
        while len(boundsQueue) != 0:
            # 取出一个查询范围
            bounds = boundsQueue.pop()  # 根据范围进行查询（百度格式：纬度，经度），默认每次最多返回20条
            baiduBounds = "%lf,%lf,%lf,%lf" % (bounds[1], bounds[0], bounds[3], bounds[2])
            data = self.baiduAPIService.placeSearchBatch(keyWords, baiduBounds)
            logger.info("bounds:%s , size: %s" % (bounds, len(data['results'])))
            if data.has_key('results'):
                # 四分法遍历： 如果范围的poi等于20,就切割该范围,并将切割后的子范围置入队列
                if len(data['results']) == 20:
                    if (bounds[2] - bounds[0]) < step or (bounds[3] - bounds[1]) < step:
                        continue

                    logger.info("split bounds, boundsQueue %s" % len(boundsQueue))
                    splitedBounds = GeoUtil().splitBounds(bounds, polygon)
                    boundsQueue.extend(splitedBounds)
                    continue
                else:
                    # 小于20 存储
                    logger.info("save place %s " % len(data['results']))
                    self.baiduMapDAO.savePlace(tableName, data)

    def fetchAddressNode(self, index, points, tableName="AddressNode", start=0, placeTableName=None):
        '''
        根据点集调用反向地址编码抓取AddressNode
        '''
        total = len(points)
        logger.info('total points:%s,start:%s ' % (str(total), str(start)))
        pageSize = 1000

        # 并发数控制：每发送3000条，暂停2秒
        # print "Start : %s" % time.ctime()
        #     if (i>0) and i%3000==0:
        #          print 'sleep 2s for index %s '% i
        #          time.sleep(2)
        for start in range(start, total, pageSize):
            logger.info("thread%s ,begin:%s, total:%s" % (str(index), str(start), str(total)))
            locationList = points[start:start + pageSize]
            respList = self.baiduAPIService.reverseGeocodingBatch(locationList=locationList)

            addressDataList = []
            for resp in respList:
                if resp['status'] == 0:
                    data = resp['result']
                    addressDataList.append(data)
            self.baiduMapDAO.saveAddressNode(tableName, addressDataList)
            if placeTableName != None:
                self.baiduMapDAO.saveAddressNodePois(placeTableName, addressDataList)
    # 清空AddressNode表
    def truncateAddressNode(self):
        self.baiduMapDAO.truncateAddressNode("AddressNode")

    def setNullStrToNull(self,tableName):
        self.baiduMapDAO.setNullStrToNull(tableName)

if __name__=="__main__":
    baiduMapSnatcherService = BaiduMapSnatcherService("localhost","xiecheng","root","1234")
    baiduMapSnatcherService.getdata()
    # print math.sin(30)