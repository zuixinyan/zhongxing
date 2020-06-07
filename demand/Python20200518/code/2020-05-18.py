# coding:utf-8 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans  
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from efficient_apriori import apriori
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

#kmeans聚类
DataFrame_info = pd.DataFrame([[1,1]
                              ,[2,1]
                              ,[1,2]
                              ,[2,2]
                              ,[4,3]
                              ,[5,3]
                              ,[4,4]
                              ,[5,4]])

kmeans = KMeans(n_clusters=2)
kmeans.fit(DataFrame_info) 
#画图
plt.figure(figsize=(8, 10))  
colors = ['b', 'g', 'r']  
markers = ['o', 's', 'D']  
for i, l in enumerate(kmeans.labels_):  
    plt.plot(DataFrame_info.iloc[i, 0]
            ,DataFrame_info.iloc[i, 1]
            ,color=colors[l]
            ,marker=markers[l]
            ,ls='None')  
plt.show()  


#实验2knn的实验
#读取数据
DataFrame_info = pd.read_csv('/Users/zhoujianjun/Downloads/workplace/2020-05-18/data/test2.csv')

#将字符类型字段转为数值
#类别字段
DataFrame_info["类别"] = DataFrame_info["类别"].replace(["矮个","中等","高个"]
                                                       , [1, 2, 3])

DataFrame_source_train = DataFrame_info.iloc[:,3:4]
DataFrame_result_train = DataFrame_info.iloc[:, 4]
#调用算法 k取5
knn_train = KNeighborsClassifier(5,'distance')
knn_train.fit(DataFrame_source_train, DataFrame_result_train)

#测试级数据Z1 刘平 女 1.62
DataFrame_source_test = pd.DataFrame([1.62])
#预测结果
DataFrame_result_test = pd.DataFrame(knn_train.predict(DataFrame_source_test))
print(DataFrame_result_test) #根据结果可知是矮个

plt.scatter(DataFrame_source_test
           ,DataFrame_result_test
           ,s=80
           ,label='all_data')
plt.scatter(DataFrame_source_test
           ,DataFrame_result_test
           ,marker='^'
           ,s=20
           ,label='test_data')
plt.legend()
plt.show()

#实验3
# 读取数据
DataFrame_info = pd.read_csv('/Users/zhoujianjun/Downloads/workplace/2020-05-18/data/test3.csv')

#定义转换函数
def Function_gettranform(parm_DataFrame
                        ,parm_column
                        ,parm_rule):
    parm_DataFrame[parm_column] = parm_DataFrame[parm_column].replace(parm_rule.keys()
                                                                     ,parm_rule.values())
    DataFrame_Result = parm_DataFrame
    return DataFrame_Result

#将特征类数据做替换
#天气
Function_gettranform(DataFrame_info, "天气", {"晴":0, "云":1,"雨":2})
#温度
Function_gettranform(DataFrame_info, "温度", {"高":0, "中":1, "低":2})
#湿度
Function_gettranform(DataFrame_info, "湿度", {"大":0, "小":1})
#风力
Function_gettranform(DataFrame_info, "风力", {"无":0, "有":1})
#类别
Function_gettranform(DataFrame_info, "类别", {"否":0, "是":1})

DataFrame_info_feature_train = DataFrame_info.iloc[:,1:-1]
DataFrame_info_score_train = DataFrame_info.iloc[:,-1]
#特征
clf_bayes = GaussianNB()
clf_bayes.fit(DataFrame_info_feature_train, DataFrame_info_score_train)

# 测试数据 Z=(天气=“晴”，温度=“高”，湿度=“小”，风力=“无”) [0,0,1,0]
print(clf_bayes.predict([[0, 0, 1, 0]]))  # 预测Z类别 结果为1 可见类别为1

print(clf_bayes.predict_proba([[0, 0, 1, 0]]))

print(clf_bayes.predict_log_proba([[0, 0, 1, 0]]))

#实验4
#读取数据
DataFrame_info = pd.read_csv('/Users/zhoujianjun/Downloads/workplace/2020-05-18/data/test4.csv').iloc[:,1]
list_info = list(map(lambda str_itmes
                      :set(str_itmes.split(','))
                      ,DataFrame_info.values.tolist()))

#获取关联规则
itemsets, rules = apriori(list_info
                        ,min_support=0.2
                        ,min_confidence=0.7)

print(rules)
