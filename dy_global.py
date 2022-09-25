import time
import sys
class Global:
    PRT_PH = sys.path[0] # 项目文件主路径
    GLabel = "0" # 0:未出结果 -1:曲线表未查到结果 -2:曲线数据格式错误 -3:曲线数据内容为空
    GIsLinux = False # 是Linux系统
    GIsTest = False # 是否测试用
    if GIsTest:
        '''公司测试'''
        ServerIP1 = "192.168.1.6"  # 螺栓基础信息服务器地址
        ServerIP2 = "192.168.1.6"  # 曲线及拧紧数据服务器地址
        LocalIP = "localhost"
        ServerUser1 = "sa"  # 螺栓基础信息服务器数据库用户名
        ServerUser2 = "sa"  # 曲线及拧紧数据服务器数据库用户名
        LocalUser = "root"
        ServerPswd1 = "Dt100000"  # 螺栓基础信息服务器数据库密码
        ServerPswd2 = "Dt100000"  # 曲线及拧紧数据服务器数据库密码
        LocalPswd = "123456"
        BoltBaseInfo_db = "BoltAnalysis_20210804"
        TighteningData_db = "Curve_yizheng"
        Curves_db = "Curve_yizheng"
        Local_db = "Tighten"
        BoltBaseInfo_label = "dbo.BoltBaseInfo"
        TighteningData_label = "Data.TighteningData"
        Curves_label = "Curve.Curves"
        Local_label = "RawData"
    else:
        '''现场使用'''
        ServerIP1 = "172.21.12.111"  # 螺栓基础信息服务器地址
        ServerIP2 = "172.21.12.112"  # 曲线及拧紧数据服务器地址
        # ServerIP2 = "localhost"
        LocalIP = "localhost"
        ServerUser1 = "sa"  # 螺栓基础信息服务器数据库用户名
        ServerUser2 = "sa"  # 曲线及拧紧数据服务器数据库用户名
        LocalUser = "root"
        ServerPswd1 = "biw50277248"  # 螺栓基础信息服务器数据库密码
        ServerPswd2 = "biw50277248"  # 曲线及拧紧数据服务器数据库密码
        LocalPswd = "123456"
        BoltBaseInfo_db = "BoltAnalysis"
        TighteningData_db = "Curve_Meb"
        Curves_db = "Curve_Meb"
        Local_db = "Tighten"
        BoltBaseInfo_label = "dbo.BoltBaseInfo"
        TighteningData_label = "Data.TighteningData"
        Curves_label = "Curve.Curves"
        Local_label = "RawData"


