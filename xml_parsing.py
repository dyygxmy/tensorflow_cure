import xml.dom.minidom as dom
class Xml_P:
    def __init__(self,xml):
        self.xml = xml
        self.doc = dom.parseString(self.xml)
        self.nodes = self.doc.documentElement
    def Parse_XML(self,nodes, key):  # layer,count,xml
        childNodes = nodes.childNodes  # 获取当前节点(ROOT)的子节点列表[PRC_SST] 这里只有一个PRC_SST
        for x in childNodes:  # 遍历子结点列
            if x.childNodes:  # 下面有子节点才处理，规避<PRT/>这类空节点
                if type(x.childNodes[0]) == dom.Element:  # 下面是Element,继续解析
                    if x.nodeName == key:  # 读到指定结点，返回节点
                        return x
                    else:  # 没读到节点，继续递归循环来拆解
                        node = self.Parse_XML(x, key)
                        if type(node) is dom.Element:  # 到这里说明递归调用有返回，判断返回的是Element，则把节点返回出去
                            return node
                # elif type(x.childNodes[0]) == dom.Text: # 下面是Text，直接取值(测试用)
                #     data = {}
                #     data[nodes.nodeName] = x.nodeValue # 值的node是 [<DOM Text node "'21'">]，所以是取列表第1个元素的data
                #     # print("thisData :",data) # 只是做个打印测试，没必要这样取

    def getValue(self,init, key_last, key_value):
        if key_last:
            index = self.Parse_XML(init, key_last)
        else:
            index = init
        datas = []
        childNodes = index.childNodes
        for x in childNodes:
            if x.childNodes:  # 防止空node 例如:<PRT/>(首尾都写一起了)
                if x.nodeName == key_value:
                    if type(x.childNodes[0]) == dom.Element:  # 下面是Element，保存到列表后面再解析
                        datas.append(x)
                    elif type(x.childNodes[0]) == dom.Text:  # 下面是Text，直接取值
                        return x.childNodes[0].nodeValue
        if len(datas) > 0:
            return datas
        else:
            return ""

    def get_IIO(self):
        IIO = self.getValue(self.nodes, "FAS", "IIO")  # 不想一层层拆解，需要指定上一层
        return IIO

    def get_curve(self):
        tighten_curve = ""
        angle_curve = ""
        TIP_list = self.getValue(self.nodes, "GRP", "TIP")  # 有可能会有多个TIP，放到循环内处理
        for tip in TIP_list:
            BLC_list = self.getValue(tip, "", "BLC")  # 一个TIP内也可能有多个BLC，也要放循环里处理 一层层下来的，不需要指定上一层
            for blc in BLC_list:
                CUR_list = self.getValue(blc, "", "CUR")  # 一层层下来的，不需要指定上一层
                for cur in CUR_list:
                    SMP_list = self.getValue(cur, "", "SMP")  # 一层层下来的，不需要指定上一层
                    for smp in SMP_list:
                        Y1V = self.getValue(smp, "", "Y1V")  # 扭矩曲线 一层层下来的，不需要指定上一层
                        XVA = self.getValue(smp, "", "XVA")
                        # print("Y1V:\n",Y1V)
                        # print("XVA:\n", XVA)
                        tighten_curve += Y1V + " "
                        angle_curve += XVA + " "
        tighten_curve = tighten_curve.rstrip()  # 去掉最后多余的空格
        angle_curve = angle_curve.rstrip()
        return (tighten_curve,angle_curve)



'''
    # 解析xml报文取值
    doc = dom.parseString(data_curve)
    nodes = doc.documentElement
    # data_xml = Parse_XML(nodes,"PNR")
    # print("getchildnode:",data_xml.childNodes)
    # print("getXML:",type(data_xml),data_xml,data_xml.childNodes[0].nodeValue,data_xml.toxml()) # getXML: <DOM Element: GRP at 0x1f3f2039670> <GRP><PNR>21</PNR>...(后面省略)

    list_TIP = getValue(nodes, "GRP", "TIP")
    # print("list_TIP:",list_TIP)
    for x in list_TIP:
        basic_data = []
        KNR = getValue(x, "", "KNR")  # 通道号
        basic_data.append(KNR)
        print("通道号(KNR):", KNR)
        PRG = getValue(x, "", "PRG")  # 程序号
        basic_data.append(PRG)
        print("程序号(PRG):", PRG)
        CSR = getValue(x, "", "CSR")  # 循环号
        basic_data.append(CSR)
        print("循环号(CSR):", CSR)
        DAT = getValue(x, "", "DAT")  # 日期
        basic_data.append(DAT)
        print("日期(DAT):", DAT)
        TIM = getValue(x, "", "TIM")  # 时间
        basic_data.append(TIM)
        print("时间(TIM):", TIM)
        STA = getValue(x, "", "STA")  # 拧紧格式
        print("拧紧格式(STA):", STA)
        result = ""
        if PRG == "99":
            result = "NOK"
        else:
            if STA == "IO":
                result = "OK"
            elif STA == "NIO": # 单独列出来，方便以后有更多的格式选项
                result = "NOK"
            else:
                result = "NOK"
        basic_data.append(result)
        print("拧紧结果:",result)

        BLC = getValue(x,"","BLC")
        for blc in BLC:
            tighten_data = []
            PRO = getValue(blc,"","PRO")
            for pro in PRO:
                MAR = getValue(pro,"","MAR")
                for mar in MAR:
                    NAM = getValue(mar,"","NAM")
                    if NAM == "MI": # 取扭矩值
                        VAL = getValue(mar, "", "VAL")  # 值
                        UNT = getValue(mar, "", "UNT")  # 单位
                        tighten_data.append(VAL+UNT)
                        print("扭矩(MI):",VAL,UNT)
                    if NAM == "WI": # 取角度值
                        VAL = getValue(mar, "", "VAL")  # 值
                        UNT = getValue(mar, "", "UNT")  # 单位
                        tighten_data.append(VAL+UNT)
                        print("角度(WI):",VAL,UNT)
            CUR = getValue(blc,"","CUR")
            for cur in CUR:
                SMP = getValue(cur,"","SMP")
                for smp in SMP:
                    Y1V = getValue(smp,"","Y1V") # 扭矩曲线
                    tighten_data.append(Y1V)
                    print("扭矩曲线(Y1V):",Y1V)
            data_all = basic_data + tighten_data
            print("oneLine:",len(colum),len(data_all),data_all)
            df = pd.DataFrame(data=[data_all])
            df.to_csv(r'data\拧紧结果.csv',encoding='utf8',mode='a',header=False,index=False) # append的写入模式，不要列号，不要行号
'''
