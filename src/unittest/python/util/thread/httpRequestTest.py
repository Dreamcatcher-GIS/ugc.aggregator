#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process, Pool
import copy_reg
import types

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

class Klass(object):
    def __init__(self):
        print "Constructor ... %s" % multiprocessing.current_process().name

    def __del__(self):
        print "... Destructor %s" % multiprocessing.current_process().name

    def func(self, x):
        print(x * x)


    def run(self):
        pool = multiprocessing.Pool(processes=3)
        for num in range(8):
            pool.apply_async(self.func, args=(num,))
        pool.close()
        pool.join()


if __name__ == '__main__':
    _kls = Klass()
    _kls.run()