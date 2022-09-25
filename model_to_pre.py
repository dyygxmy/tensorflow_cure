import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # 不打印大量的警告信息
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import numpy as np
import pandas as pd
import joblib
from dy_global import Global as GL

class Model:
    def __init__(self,path):
        self.model = self.get_model(path)

    def get_model(self,path):
        my_model = load_model(path)
        return my_model

    '''数值化'''
    def label_to_num(self,data):
        le = LabelEncoder()
        data = data.copy()
        data['扭矩值'] = le.fit_transform(data.loc[:, '扭矩值'])
        # data['拧紧结果'] = le.fit_transform(data.loc[:, '拧紧结果'])
        data.loc[data['拧紧结果'] == "OK", "拧紧结果"] = 1
        data.loc[data['拧紧结果'] == "NOK", "拧紧结果"] = 0
        return data

    '''归一化'''
    def num_to_min_max(self,data):
        mm = joblib.load('%s/scalar01'%GL.PRT_PH)
        # mm = MinMaxScaler()
        x = data[['shake_num', 'shake_num_0.2_4', '拧紧结果', '扭矩值', 'IIO', 'shake_to_bottom']]
        # x = data[['shake_num', 'shake_num_0.2_4', 'tighteningstatus', '扭矩值', 'iio', 'shake_to_bottom']]
        # x = mm.fit_transform(x)
        x = mm.transform(x)
        # y = np.array(data['label'])
        return x

    '''数值化标签退化'''
    def label_back(self,y_pred, s=np.array(['OK', 'high', 'low', 'medium'], dtype=object)):
        # s = label_le.classes_
        dic_label = []
        for i in y_pred:
            # dic_label.append(i)   #查看标签符号
            dic_label.append(s[i])
        dic_label_df = pd.DataFrame(dic_label)
        dic_label_df.rename({0: u'predict_temp'}, axis=1, inplace=True)
        return dic_label_df

    '''将螺栓号未分离/Siemens/predict的信息统一成一列'''
    '''20210907根据MQFA2要求, 将安装转向关注开关屏蔽为low risk,但在原始预测中保留算法的真实结果'''
    # def label_final(self,df):
    #     temp_label = []
    #     df_label = df[['螺栓号是否分离', 'operator', 'tighteningstatus', 'predict_temp', '装配内容']]
    #     for index, rows in df_label.iterrows():
    #         if rows['operator'] == 'Siemens':
    #             temp_label.append('No curve data')
    #         elif rows['螺栓号是否分离'] == 0:
    #             temp_label.append('Low risk')
    #         elif rows['tighteningstatus'] == 'NOK':
    #             temp_label.append('Risk NOK')
    #         elif rows['装配内容'] == '安装转向管柱开关':
    #             temp_label.append('Low risk')
    #         else:
    #             temp_label.append(rows['predict_temp'])
    #     final_label_df = pd.DataFrame(temp_label)
    #     final_label_df.rename({0: u'predict'}, axis=1, inplace=True)
    #     return final_label_df

    def get_label(self,df):
        # 选择需要的列
        data = df[['ID', 'shake_num', 'shake_num_0.2_4', 'shake_to_bottom','拧紧结果','扭矩值','IIO']]
        # data = df[['recordid', 'shake_num', 'shake_num_0.2_4', 'shake_to_bottom', 'tighteningstatus', '扭矩值', 'iio']]
        # print("原始表:\n",data)
        #数值化
        data = self.label_to_num(data)

        #归一化
        x = self.num_to_min_max(data)

        # 预测结果 获取label的数值化标签
        # y_pred = self.model.predict_classes(x) # AttributeError: 'Sequential' object has no attribute 'predict_classes'
        y_pred = np.argmax(self.model.predict(x), axis=-1) #  [0,1,2,3]

        # 转换对应标签
        # label_back_df = self.label_back(y_pred) # ['OK', 'high', 'low', 'medium']

        # print("获取label的标签:",y_pred,"\n",label_back_df)
        return y_pred

    '''读取训练模型h5, 并预测风险'''
    def model_predict(self,df_result):
        data = df_result[
            ['ID', 'shake_num', 'shake_num_0.2_4', '拧紧结果', '扭矩值', 'IIO', 'shake_to_bottom']]
        # data = NN.data_dichotomy(data)      # 二值化
        data = self.label_to_num(data)  # 数值化
        x = self.num_to_min_max(data)  # 归一化
        # y_pred = my_model.predict_classes(x)  # 预测
        y_pred = np.argmax(self.model.predict(x), axis=-1)  # 预测
        label_back_df = self.label_back(y_pred, s=np.array(['OK', 'Risk']))  # 标签返回
        df_result = pd.concat((df_result, label_back_df), axis=1)  # 合并
        # final_label_df = self.label_final(df_result)  # 将siemos/螺栓号未分离的点位标识出
        # df_result = pd.concat((df_result, final_label_df), axis=1)  # 再次合并
        return df_result
