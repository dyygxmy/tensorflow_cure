import numpy as np
import pandas as pd

'''拼接主表与辅助表'''
def combine_data(df,df_add_abstract):
    df_result = pd.merge(df, df_add_abstract, left_on='螺栓编号', right_on='螺栓编号')
    return df_result


'''消除连续未断开的数据'''
def clear_continuous_number(ang_value):
    tor = []
    for k in range(len(ang_value)):
        try:
            ang_value[k] = float(ang_value[k])
            tor.append(ang_value[k])
        except:
            ang_value[k] = ang_value[k-1]
    return tor


'''定义函数计算工艺的抖动的次数'''
def compute_shake_num(tor, diff_threshold=0.25, init_tor =3):  # ang没有赋值
    # 筛选torvalue > 1的
    tor = [y for y in tor]  # if float(y)>= 1
    # 空值的处理
    if tor == []:
        max_tor = 0
    else:
        max_tor = np.max(tor)
    # 计算抖动次数
    shake_num = 0
    # 记录异常点位坐标
    tor_shake_point = []
    tor_axis = []

    for i in range(len(tor) - 1):
        if float(tor[i]) >= init_tor:
            if tor[i] == max_tor:
                break
            # 前后两次抖动差距大于 diff_threshold
            elif tor[i] > tor[i + 1] * (1 + diff_threshold):
                shake_num += 1
                tor_shake_point.append(tor[i])
                tor_axis.append(i)
    return tor_shake_point, tor_axis, shake_num  # ang_shake_point,


'''拟合抖动 默认系数0.4 3'''
def calculator_data(df,lenth):
    shake_freq = []
    for i in range(lenth):
        y = df.loc[i, '扭矩曲线']
        y = str(y).split(',')
        y = clear_continuous_number(y) # 消除连续未断开的数据
        tor = y
        if y != 0:
            tor_shake_point, tor_axis, shake_num = compute_shake_num(tor, diff_threshold=0.4) # 定义函数计算工艺的抖动的次数
            shake_freq.append(shake_num)
        elif y == 0:
            shake_freq.append(0)
    result = pd.concat((df, pd.DataFrame(shake_freq)), axis=1)
    result.rename({0: u'shake_num'}, axis=1, inplace=True)
    print('-------------------------Finish calculator_data---------------------------')
    return result


'''ML提取抖动其余的特征值'''
def add_shake_indicator(df,threshold=0.3,in_tor =1):
    shake_freq = []
    for i in range(len(df)):
        y = df['扭矩曲线'][i]
        y = str(y).split(',')
        y = clear_continuous_number(y) # 消除连续未断开的数据
        tor = y
        if y !=0:
            tor_shake_point,tor_axis,shake_num = compute_shake_num(tor,diff_threshold=threshold, init_tor = in_tor ) # 定义函数计算工艺的抖动的次数
            shake_freq.append(shake_num)
        elif y ==0:
                shake_freq.append(0)
    df = df.reset_index(drop=True)
    shake_freq = pd.DataFrame(shake_freq).reset_index(drop=True)
    result = pd.concat((df,shake_freq),axis=1)
    result.rename({0:u'shake_num_%s_%s'%(threshold,in_tor)},axis=1,inplace=True)
    return result


'''计算正常运行后,是否存在降到底部的情况'''
def compute_shake_to_bottom(tor, init_tor =3):  # ang没有赋值
    # 筛选torvalue > 1的
    tor = [y for y in tor]  # if float(y)>= 1
    #print('tor=\n', tor)
    #     ang = [x for x in ang]
    # 空值的处理
    if tor == []:
        max_tor = 0
    else:
        max_tor = np.max(tor)
        init_tor = max_tor*0.3
    # 记录异常点位坐标
    tor_shake_point = []
    tor_axis = []

    start = False
    max_continues_bottom = 0
    continues_bottom = 0 # 计算落到底部的点的个数
    for i in range(len(tor) - 1):
        # 如果落到底部在前20%区域,先忽略
        if i < len(tor) * 0.2:
            continue
        # 判断是否已经正常启动,设置start=True
        if float(tor[i]) >= init_tor:
            start = True
            if tor[i] == max_tor:
                break

        # 之前已经达到了 init_tor
        if start:
            if float(tor[i]) <= max(0.2, max_tor*0.03):
                continues_bottom = continues_bottom + 1
                if continues_bottom > max_continues_bottom:
                    max_continues_bottom = continues_bottom
                tor_shake_point.append(tor[i])
                tor_axis.append(i)
            else:
                continues_bottom = 0

    return tor_shake_point, tor_axis, max_continues_bottom  # ang_shake_point,


'''添加坠落到底的新特征,并添加至df中'''
def add_shake_to_bottom_indicator(df):
    # 计算shake_to_bottom特征
    df['shake_to_bottom'] = 0
    for index, row in df.iterrows():
        torquearray = row['扭矩曲线']
        y = str(torquearray).split(',')
        y = clear_continuous_number(y)
        tor_shake_point, tor_axis, shake_to_bottom = compute_shake_to_bottom(y)
        df.loc[index, 'shake_to_bottom'] = shake_to_bottom
    # print('add_shake_to_bottom_indicator done!', '-->', datetime.datetime.now())
    #print("df:\n",df)
    return df