import time
from dy_global import Global as GL
import pymssql as sql
class Sql_M:
    def connectSql(self,ip, user, pasd, db):  # 连接数据库
        try:
            connt = sql.connect(host=ip,
                                user=user,
                                password=pasd,
                                database=db,
                                charset="utf8",
                                autocommit=True
                                )
            if connt:
                print("连接%s成功" % db)
            return connt
        except:
            time.sleep(2)
            return False

    def executeSql(self,sql, db, type=""):
        connt = None
        if db == GL.BoltBaseInfo_db:
            connt = self.connectSql(GL.ServerIP1, GL.ServerUser1, GL.ServerPswd1, db)
        else:
            connt = self.connectSql(GL.ServerIP2, GL.ServerUser1, GL.ServerPswd2, db)
        if connt:
            cursor = connt.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
            cursor.execute(sql)  # 执行sql语句
            datas = []
            if type == 'select':
                row = cursor.fetchone()  # 读取查询结果,
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
            return datas

    # def createTable(self):
    #     sql = "create table CurveAnalysisResult(id varchar(20))"
    #     db = "CurveAnalysisResult"
    #     self.executeSql(sql, db)
    #
    # def insertSql(self):
    #     sql = "insert into CurveAnalysisResult (id, name, sex)values(1002, '张si', '女')"
    #     db = "CurveAnalysisResult"
    #     self.executeSql(sql, db)
    #
    # def deleteSql(self):
    #     sql = "DELETE * FROM dbo.CurveAnalysisResult WHERE id = 156"
    #     db = "CurveAnalysisResult"
    #     self.executeSql(sql, db)

    def selectSql(self,sql, db):
        datas = self.executeSql(sql, db, "select")  # 执行sql语句
        return datas

    def updateSql(self,sql,db):
        self.executeSql(sql,db,"update")