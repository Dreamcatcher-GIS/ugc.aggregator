# -*- coding:utf-8 -*-
__author__ = 'DreamCathcer'

import traceback
import csv
import re

from util.io.CSVFileUtil import CSVFileUtil
from service.map.baidu.APIService import BaiduMapAPIService

input_file = r'C:\Users\kaipeng\Desktop\rent.csv'
output_file = r"C:\Users\kaipeng\Desktop\rent_geocode.csv"
have_title = True
handle_row_index = 2

def handle_text(text):
    return "广州市".decode("utf-8").encode("gbk")+re.sub("[\[\]]","",text)

if __name__=="__main__":
    csv_file_util = CSVFileUtil()
    map_service = BaiduMapAPIService("WBw4kIepZzGp4kH5Gn3r0ACy")
    writer = csv.writer(file(output_file, "wb"))
    count = 0
    for line in csv_file_util.reader(file(input_file)):
        count += 1
        if have_title and count==1:
            continue
        geocoding_info = map_service.doGeocoding(handle_text(line[handle_row_index]))
        try:
            coord = str(geocoding_info["result"]["location"]["lng"])+','+str(geocoding_info["result"]["location"]["lat"])
            line[3] = coord
            print "Success:count:%d"%count
        except:
            traceback.print_exc()
            print "Error:count:%d"%count
            continue
        finally:
            writer.writerow(line)

