# coding=utf8
import multiprocessing
import time

from util.common.CollectionUtil import CollectionUtil
from util.io.FileUtil import FileUtil
import logging
import logging.config

logging.config.fileConfig(FileUtil().getLogConfigPath())
logger = logging.getLogger("ugc")

def worker(msg):
        print "msg:", msg
        time.sleep(3)
        print "end"
        return "done " + msg

class MultiProcessingTest(object):

    def __init__(self):
        print "Constructor "
        self.pointList = []

    def process(self):
        try:
            pool = multiprocessing.Pool(processes=4)
            result = []
            for i in xrange(3):
                msg = "hello %d" % (i)
                result.append(pool.apply_async(worker, (msg,)))
            pool.close()
            pool.join()
            for res in result:
                print ":::", res.get()
            print "Sub-process(es) done."
        except:
            pass


if __name__ == "__main__":
    service = MultiProcessingTest()
    service.process()
