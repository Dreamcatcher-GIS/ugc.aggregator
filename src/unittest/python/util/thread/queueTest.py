import multiprocessing
import time

def func(msg):
    for i in xrange(3):
        print msg
        time.sleep(1)

def main():
    pool = multiprocessing.Pool(processes=4)
    for i in xrange(10):
        msg = "hello %d" %(i)
        pool.apply_async(func, (msg, ))
    pool.close()
    pool.join()
    print "Sub-process(es) done."

if __name__ == '__main__':
   main()