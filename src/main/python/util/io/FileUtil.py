# -*- coding:utf-8 -*-
__author__ = 'geosmart'
import sys, os
import pickle
import io

class FileUtil(object):
    def __init__(self):
        pass

    """
    将python对象写入文件
    """
    def writeObjToFile(self,fileName,obj):
        with open(fileName, 'wb') as f:
            pickle.dump(obj, f)

    """
    从文件读取python对象
    """
    def readFileToObj(self,fileName):
        if os.path.exists(fileName):
            with open(fileName, 'rb') as f:
                obj = pickle.load(f)
                return obj

    """
    删除文件
    """
    def deleteFile(self,fileName):
        if os.path.exists(fileName):
            os.remove(fileName)
    """
    获取脚本文件的当前路径
    """

    def cur_file_dir(self):
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    """
    获取logging配置文件的路径
    """

    def getLogConfigPath(self, rootFolder="ugc.aggregator"):
        logPath = self.cur_file_dir().split(rootFolder, 1)[0] + rootFolder + "/src/main/scripts/logging.ini"
        # print logPath
        return logPath
