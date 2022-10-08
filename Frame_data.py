# 本类处理DataFrame数据
import pandas as pd
class Frame:
    def __init__(self,df):
        self.df = df

    def list_to_frame(self):
        keys = self.df.keys()
        all_data = []
        for x in range(len(self.df)):
            oneline = []
            for i in range(len(keys)):
                oneline.append(self.df.loc[x, keys[i]])
            all_data.append(oneline)
        df = pd.DataFrame(all_data,columns=keys)
        return df

