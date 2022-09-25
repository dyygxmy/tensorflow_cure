import time

class Print_Time:
    def __init__(self,c):
        self.count = c

    def print(self,count,msg=None):
        self.count = count
        time_current = time.time()
        locale_time = time.localtime(time_current)
        msec = int(time_current * 1000 % 1000)
        print("[%d] %s:%s:%s:%d" % (self.count,locale_time.tm_hour, locale_time.tm_min, locale_time.tm_sec, msec),msg)