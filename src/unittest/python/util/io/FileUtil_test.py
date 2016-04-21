# -*- coding:utf-8 -*-
import os
import shutil
import unittest

# from util.io.FileUtil import FileUtil
from util.io.FileUtil import FileUtil


class FileUtil1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "setUpClass..."

    @classmethod
    def tearDownClass(cls):
        print "tearDownClass..."

    def test_getLogConfigPath(self):
        path=FileUtil().getLogConfigPath()
        print path

    def test_readDirFiles(self):
        path="c:/data/test/"
        fileNames=os.listdir(path)

        path_bak="c:/data/cache_bak/"
        for fileName in fileNames:
            file=path+fileName
            print  file
            myList=FileUtil().readFileToObj(file)
            print len(myList)

            print  "copy  to bak path"
            shutil.copy(file,path_bak)
            # TODO 读取完后文件剪切到新目录
        pass

    def test_writeObjToFile(self):
        path="c:/data/test/"
        if os.path.exists(path)==False :
            os.makedirs(path)
        filePath=path+"pointListCache.txt"
        myList=[118.12,32.23,118.122,32.211]
        FileUtil().writeObjToFile(filePath,myList)

        myList=[218.12,32.23,218.222,32.211]
        FileUtil().writeObjToFile(filePath,myList)
        myList=FileUtil().readFileToObj(filePath)
        print  myList

if __name__=="__main__":
    unittest.main()

