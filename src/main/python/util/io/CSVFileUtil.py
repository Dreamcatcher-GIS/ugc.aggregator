# -*- coding:utf-8 -*-
__author__ = 'LiuYang,geosmart'

import csv


class CSVFileUtil(object):

    def reader(self, file):
        for line in csv.reader(file):
            yield line

    def writer(self,file):
        return csv.writer(file)

if __name__ == "__main__":
    csv_file_util = CSVFileUtil()
    for line in csv_file_util.reader(file(r'C:\Users\kaipeng\Desktop\rent.csv','rb')):
        print line[2]
