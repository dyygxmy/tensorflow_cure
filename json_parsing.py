import json
import xmltodict
class Json_P:
    '''
    用来解析Json格式数据
    '''
    def Parse_json(self,jd,key):
        if type(jd) is dict:
            for j in jd:
                if j == key:
                    return jd[j] # 层层递归，返回不到最外层，只能去上层处理
                else:
                    getValue = self.Parse_json(jd[j],key)
                    if getValue:
                        return getValue # 逻辑中只有解析GRP时才有返回值，取出来层层返回出去到最外层
# 用xmltodict工具可以直接把xml数据转换成json格式
# xml解析器
# xml_par = xmltodict.parse(data)
# # # 通过dumps()方法转换成json,格式化json，index=1
# json_all = json.dumps(xml_par, indent=1)
# # print(json_all)
# json_all = json.loads(json_all)
# getJson = Parse_json(json_all,"GRP")
# print("getJson :",getJson) # getJson : {'PNR': '21', 'VEN': 'BOS', 'TYP': 'KE350',...(后面省略)