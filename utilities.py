#coding=utf-8
import para
import csv
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

class DataLoader:
    def __init__(self):
        self.t = ['M'] + ['i4'] + ['f4']*15+['i4']+['f4']*3+['i4']+['f4']*26+['i4']+['f4']*5+['i4']+['f4']*12+['i4']+['f4']*2

    def __call__(self, train_data_path, machine_num):
        file_path = train_data_path +  '{0:03d}'.format(machine_num+1) + '/201807.csv'
        data = np.loadtxt(file_path,dtype=np.str,delimiter=',',skiprows=1)
        mask = (data!='').all(axis=1)
        full_data = data[mask]
        p_miss_data = data[np.logical_not(mask)]
            
        # record to be filled
        file_path = train_data_path+'template_submit_result.csv'
        data = np.loadtxt(file_path,dtype=np.str,delimiter=',',skiprows=1)
        mask = data[:,1]==str(machine_num)
        all_miss_data = data[mask]

#         raw_data_str = np.array(full_data)
#         raw_data = full_data

#         for i in range(70):
#             s = raw_data_str[:,i].astype(self.t[i])
#             raw_data.append(s)

        return full_data,[p_miss_data,all_miss_data]


# class used for pre-process data 
class PreProc:
    def __init__(self, data, types):
        self.features = [True if t=='f4' else False for t in types] # 68个字段预处理分类操作
        self.continuous, self.discrete = self.classify(data)
        self.proc_cont = self.standardization(self.continuous)
        self.proc_disc = self.one_hot(self.discrete)
        
    def classify(self, data):
        return data[:,self.features], data[:,np.logical_not(self.features)]
        
    def standardization(self, data):
        self.stda = StandardScaler()
        data = data.astype('f4')
        data = (data - data.mean()) / (data.max() - data.min())
        return data
        
    def one_hot(self,data):
        self.enc = OneHotEncoder(categories='auto')
        data = data.astype('i4')
        return self.enc.fit_transform(data).todense()
