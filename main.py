from myLog import MyLog as LOG
LOG.print("main start")
import sys
import time
# from print_time import Print_Time as P_T
from dy_global import Global as GL
# LOG.print(0)
import pandas as pd
from sqlalchemy import create_engine
# pd.set_option("display.max_rows", 1000) # 可显示1000行
# pd.set_option("display.max_columns", 1000)  # 可显示1000列
# pd.set_option('display.max_rows', None) # 显示全部行
pd.set_option('display.max_columns', None)  # 显示全部列
# pd.options.display.max_rows = 300   # 最大显示300行


import Data_clean as cl
# LOG.print(1)

from sql_manage import Sql_M as Sql
# LOG.print(2)

from xml_parsing import Xml_P as Xml
# LOG.print(3)

# LOG.print(4)


from dy_global import Global as G_
# LOG.print(5)

def get_bolt_frame(sql):
    '''此方法用来从数据库中读取螺栓基础信息后整合成frame数据返回给调用者'''
    bolt_head_list = ["装配内容", "扭矩值", "公差", "螺栓编号"]
    bolt_info_list = []
    # 提取螺栓基础信息
    db_bolt = GL.BoltBaseInfo_db
    select_bolt = "SELECT AssemblyContent,TorqueValue,ToleranceRange,BoltID FROM %s"%GL.BoltBaseInfo_label
    datas_bolt = sql.selectSql(select_bolt, db_bolt)
    for x in datas_bolt:
        AssemblyContent = x[0]
        TorqueValue = x[1]
        ToleranceRange = x[2]
        BoltID = x[3]
        line = [AssemblyContent, TorqueValue, ToleranceRange, BoltID]
        bolt_info_list.append(line)

    # 数据库中提取的螺栓基础信息bolt_info_list生成frame数据
    df_add = pd.DataFrame(bolt_info_list, columns=bolt_head_list)  # 导入螺栓基础数据
    # LOG.print("df_add:\n",df_add)
    return df_add
TighteningTime_set = ""
def get_tighten_frame(sql):
    '''此方法用来从数据库中的拧紧表及曲线表然后整合两表的数据生成frame数据返回给调用者'''
    global TighteningTime_set
    tighten_head_list = ["ID", "车码", "螺栓编号", "IIO", "拧紧结果", "扭矩曲线","角度曲线"]
    tighten_info_list = []
    # 遍历拧紧表里未生成label的数据，每次只处理一条
    db_tighten = GL.TighteningData_db
    # 按数据产生顺序一条一条的刷
    select_tighten = "SELECT TOP 1 RecordID,IDCode,ScrewID,TighteningStatus,CurveID,TighteningTime FROM %s where Label IS NULL and Station in ('076R-1','080R','085R-1','093R-2') order by RecordID"%GL.TighteningData_label
    # 一次刷新最新的200条数据
    # select_tighten = "SELECT TOP 200 RecordID,IDCode,ScrewID,TighteningStatus,CurveID,TighteningTime FROM %s where Station in ('076R-1','080R','085R-1','093R-2') order by RecordID DESC"%GL.TighteningData_label
    datas_tighten = sql.selectSql(select_tighten, db_tighten)
    # LOG.print(12,datas_tighten)
    if datas_tighten: # 有需要处理的拧紧数据
        ID = datas_tighten[0][0]
        VIN = datas_tighten[0][1].strip()
        BoltID = datas_tighten[0][2].strip()
        IsOK = datas_tighten[0][3].strip()
        CurveID = datas_tighten[0][4]
        TighteningTime_set = datas_tighten[0][5].strftime("%Y-%m-%d %H:%M:%S")
        # print('---->',TighteningTime_set)
        # LOG.print(11,VIN) # 打印每次取数的时间

        # 提取对应的曲线数据
        db_curve = GL.Curves_db
        select_curve = "SELECT * FROM %s WHERE RecordID = %d"%(GL.Curves_label,CurveID)
        datas_curve = sql.selectSql(select_curve, db_curve)
        id_curve = ""
        IIO = ""
        tighten_curve = ""
        angle_curve = ""
        if len(datas_curve) > 0: # 有对应的曲线数据
            id_curve = datas_curve[0][0]
            data_curve = datas_curve[0][1]
            #print("data_curve:",data_curve[:30])
            #xml = Xml(data_curve)
            if data_curve:
                G_.GLabel = '0'
                try:
                    xml = Xml(data_curve)
                    IIO = xml.get_IIO()
                    (tighten_curve,angle_curve) = xml.get_curve()
                except:
                    G_.GLabel = "-2"
            else:
                G_.GLabel = "-3"
        else:
            G_.GLabel = "-1"

        # LOG.print(13, id_curve)
        tighten_curve = tighten_curve.replace(" ",",")
        angle_curve = angle_curve.replace(" ", ",")
        line = [ID, VIN, BoltID, IIO, IsOK, tighten_curve,angle_curve] # 整合一条数据
        tighten_info_list.append(line) # 将一条数据添加到列表中


    # 数据库中提取的拧紧数据(含曲线)tighten_info_list生成frame数据
    df = pd.DataFrame(tighten_info_list, columns=tighten_head_list)
    return df

def main():
    # LOG.print(6)
    # 创建训练模型对象model
    model_path = r'%s\model\NN_slabel_classification_model_2021.h5'%G_.PRT_PH
    if G_.GIsLinux:
        model_path = '%s/model/NN_slabel_classification_model_2021.h5'%G_.PRT_PH
    # print("model_path",model_path,G_.GIsLinux)
    from model_to_pre import Model as Mo # 大概将近4秒
    model = Mo(model_path) # 训练模型加载 将近1秒
    # LOG.print(7)
    sql = Sql() # 创建sql对象
    # LOG.print(8)
    cycle = 0
    last_None = True # 上一次没数据
    label = ""
    while True:
        df = get_tighten_frame(sql) # 获取拧紧数据的frame数据
        # LOG.print(10,len(df))
        if len(df) > 0:
            if last_None: # 刚才没有需要计算的拧紧数据，突然来数据了，马上更新螺栓基础信息
                cycle = 0
            cycle += 1
            #df_add = None
            if cycle == 1:
                df_add = get_bolt_frame(sql) # 获取螺栓基础信息frame数据
                # LOG.print(9,len(df_add))
            if cycle == 20: # 正常处理数据过程中，20次循环更新一次螺栓基础信息
                cycle = 0
            last_None = False
            # 提取raw data 特征值 计算 shake_num 及 shake_num_0.2_4
            result = cl.calculator_data(df, len(df))  # 算出 shake_num并添加到结果中 拟合抖动 默认系数0.4 3
            result = cl.add_shake_indicator(result, threshold=0.2, in_tor=4) # 算出 shake_num_0.2_4并添加到结果中 ML提取抖动其余的特征值
            result = cl.add_shake_to_bottom_indicator(result) # 计算出 shake_to_bottom
            #print("111111result\n:",result,"\n11111df_add:\n",df_add)
            # 拼接处理过后的拧紧数据表及螺栓基础信息表
            df_result = cl.combine_data(result,df_add)
            # LOG.print("拼接信息:\n",df_result)

            # 执行算法,添加预测 (没啥用，最后再去处理)
            # df_result = model.model_predict(df_result) # 计算出 predict_temp ['OK', 'Risk']
            # print("预测后:\n", df_result)
            # for x in range(len(df_result)): # 一次处理一条，不需要循环了
            if len(df_result) > 0:
                ID = df_result.loc[0, 'ID']
                BoltID = df_result.loc[0, '螺栓编号']
                VIN = df_result.loc[0, '车码']
                TighteningStatus = df_result.loc[0, '拧紧结果']
                # label = label_result.loc[0, 'predict_temp']
                if G_.GLabel == "0":
                    # 数据使用训练模型生成新结果
                    label_result = model.get_label(df_result)
                    label = label_result[0]
                else:
                    label = G_.GLabel
                LOG.print("result:",ID,label,BoltID,VIN,TighteningStatus)


                saveFrame = pd.concat((df_result,pd.DataFrame([TighteningTime_set])), axis=1)
                saveFrame.rename({0: u'拧紧时间'}, axis=1, inplace=True)
                saveFrame = pd.concat((saveFrame, pd.DataFrame([label])), axis=1)
                saveFrame.rename({0: u'Label'}, axis=1, inplace=True)
                # 原始数据写入到本地数据库
                mysqlInfo = {
                    "host": GL.LocalIP,
                    "user": GL.LocalUser,
                    "password": GL.LocalPswd,
                    "database": GL.Local_db,
                    "port": 3306,
                    "charset": 'utf8'
                }
                engine = create_engine(
                    'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)d/%(database)s?charset=utf8' % mysqlInfo,
                    encoding='utf-8')
                # engine = create_engine('mysql+pymysql://amrw:qubPbNoITJ4tDzjw@localhost1:3306/etcpdw_dev')
                saveFrame.to_sql(
                    name="RawData",
                    con=engine,
                    index=False,
                    if_exists="append"
                )

                # print("save over")
                # 添加 label 数据到拧紧数据表
                db_tighten = GL.TighteningData_db
                update_tighten = "UPDATE %s SET label = '%s' WHERE RecordID = %d"%(GL.TighteningData_label,label,ID)
                sql.updateSql(update_tighten, db_tighten)
                # 添加 label 数据到螺栓基础信息表
                db_tighten = GL.BoltBaseInfo_db
                update_tighten = "UPDATE %s SET label = '%s' , VIN_0 = '%s' , TighteningStatus_0 = '%s', " \
                                 "TighteningTime_0 = '%s' WHERE BoltID = '%s'" % (GL.BoltBaseInfo_label,label, VIN,TighteningStatus,TighteningTime_set,BoltID)
                # print('update_tighten:---->', db_tighten,update_tighten)
                sql.updateSql(update_tighten, db_tighten)
        else:
            LOG.print("NULL DATA")
            last_None = True
            time.sleep(5)


def main1():
    df_result = pd.read_excel(r".\data\原数据.xlsx")
    # from model_to_pre import Model as Mo # 大概将近4秒
    # model = Mo(r'%s\model\NN_slabel_classification_model_2021.h5' % G_.PRT_PH)  # 训练模型加载 将近1秒
    # label_result = model.get_label(df_result)
    # LOG.print("label标签:\n",model.label_back(label_result),"\nlabel数值:\n",label_result)
    new_list = []
    for x in range(len(df_result)):
        data = df_result.loc[x,"扭矩曲线"]
        new_list.append(data.replace(" ",","))
    new_df = pd.DataFrame(new_list,columns=["扭矩曲线"])
    df_result["扭矩曲线"] = new_df["扭矩曲线"]
    print(df_result)

def main2():
    df_result = pd.read_excel(r".\data\原数据.xlsx")
    result = cl.calculator_data(df_result, len(df_result))  # 算出 shake_num并添加到结果中 拟合抖动 默认系数0.4 3
    result = cl.add_shake_indicator(result, threshold=0.2, in_tor=4)  # 算出 shake_num_0.2_4并添加到结果中 ML提取抖动其余的特征值
    result = cl.add_shake_to_bottom_indicator(result)  # 计算出 shake_to_bottom
    result.to_excel(r".\data\clean_result.xlsx")

def main3():
    log = LOG("mylog")
    logger = log.setup_log()
    logger.info("this is info message")
    logger.warning("this is a warning message")
    try:
        int("xjk")
    except ValueError as e:
        logger.error(e)

def main4():
    # sql = Sql()  # 创建sql对象
    import pymssql as sql
    db = GL.TighteningData_db
    select = "SELECT * FROM dbo.test;"
    connt = sql.connect(host="192.168.101.7",
                        user="sa",
                        password="biw50277248",
                        database=db,
                        charset="utf8",
                        autocommit=True
                        )
    if connt:
        cursor = connt.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
        cursor.execute(select)  # 执行sql语句
        datas = []
        row = cursor.fetchone()  # 读取查询结果,
        print(row)
        while row:  # 循环读取所有结果
            line = []
            for x in row:
                line.append(x)  # 一行中的数据生成line列表
            datas.append(line)  # 所有列表数据添加到datas
            row = cursor.fetchone()
        connt.commit()  # 提交
        cursor.close()  # 关闭游标
        connt.close()  # 关闭连接
        print("断开%s的连接" % db)
        print("select datas:\n",datas)
    else:
        print(sql.Error)

def main5():
    import pymssql as sql
    import pandas as pd
    db = "Curve_Meb"
    select = "SELECT * FROM [Curve_Meb].[dbo].[test]"
    connt = sql.connect(host="192.168.101.7",
                        user="sa",
                        password="biw50277248",
                        database=db,
                        charset="utf8",
                        # autocommit=True
                        )
    if connt:
        print("连接成功!")
    else:
        print("连接失败!")
    df = pd.read_sql(select, con=connt)
    connt.close()
    print(df)

if __name__ == '__main__':
    main5()