import pandas as pd 
import numpy as np
import io as io 
from functools import reduce


# def download_file(input_path,chunksize,save_path):
#     	fr = open(input_path,'rb')
# 	df = pd.read_csv(fr,chunksize=chunksize,sep='\t')
# 	filename = 0
# 	rows_count=0
# 	for tmpdf in df:
# 		filename += 1
# 		print(filename)
# 		tmp_path = save_path+str(filename)+'.csv'
# 		rows_count += tmpdf.shape[0]
# 		tmpdf.to_csv(tmp_path,index=0,header=0)
# 	fr.close()
# 	return rows_count
	
# ###合并文件
# def read_file_batch(filename_list,save_path):
# 	path_list = [save_path+x for x in filename_list]
# 	result = 0
# 	tmp_df = pd.DataFrame()
# 	for filepath in path_list:
# 		fr = open(filepath,'rb')
# 		df = pd.read_csv(fr,header=None)
# 		result += df.shape[0]
# 		tmp_df = tmp_df.append(df)
# 	print(result)
# 	return tmp_df


def function_ReadFile(parm_FilePath):
    """
    @author:zhoujianjun
    @parameter: {FilePath:文件目录}
    @create_date:
    @update_date:
    @purose:使用本函数读取文件，后续可以追减文件格式。
    @commet:
    """
    dict_function = {'xlsx':'read_excel'
                    ,'xls':'read_excel'
                    ,'txt':'read_table'
                    ,'':'read_table'
                    ,'csv':'read_csv'}
    FileType = parm_FilePath.split('.')[-1]
    DataFrame_File = ''
    if FileType in dict_function.keys():
        DataFrame_File = getattr(pd,dict_function[FileType])(parm_FilePath)
    else:
        print('增加输入文件格式')
    return DataFrame_File


def function_MergeDataFrame(parm_JoinKey
                           ,parm_JoinWay
                           ,*args):
    """
    @author:zhoujianjun
    @parameter: {parm_JoinKey：关联键值，parm_JoinWay:关联方式,*args:dataframe名称}
    @create_date:
    @update_date:
    @purose:使用本函数可以对于多表关联，如果关联方式和关联键是一致的话可以使用本函数
    @commet:
    """
    list_DataFrame = list(args)
    DataFrame_MergeResult = reduce(lambda LeftTable
                                         ,RightTable
                                         :pd.merge(LeftTable
                                                  ,RightTable
                                                  ,how = parm_JoinWay
                                                  ,on = parm_JoinKey)
                                                  ,list_DataFrame)
    return DataFrame_MergeResult


def function_GetDataFrameInfo(para_DataFrame):
    """
    @author:zhoujianjun
    @parameter: {para_DataFrame:输入数据框}
    @create_date:
    @update_date:
    @purose:获取数据框的每个列的非空值率和字符类型
    @commet:
    """
    # 将数据框的每列的信息结果转为数据框格式
    str_Buffer = io.StringIO()
    para_DataFrame.info(null_counts=True
                       ,verbose=True
                       ,memory_usage='deep'
                       ,buf=str_Buffer)
    list_Info = str_Buffer.getvalue().split('\n')[3:-3]
    list_StaticInfo = list(map(lambda str_Info
                                     :(str_Info.split(' ')[0] + ' ' + \
                                      str_Info.split(' ')[-3] + ' ' + \
                                      str_Info.split(' ')[-1]).split(' ')
                                     ,list_Info))
    DataFrame_StaticInfo = pd.DataFrame(list_StaticInfo
                                       , columns=['ColumnName', 'NonNA_Rows', 'Dtype'])
    # 获取行数
    DataFrame_StaticInfo['TotalRows'] = para_DataFrame.shape[0]
    # 获取每个列非空占比
    DataFrame_StaticInfo['Saturation_Ratio'] = DataFrame_StaticInfo['NonNA_Rows'].apply(int) / DataFrame_StaticInfo['TotalRows']
    # 将字符类型做转换
    DataFrame_StaticInfo['Dtype'] = DataFrame_StaticInfo['Dtype'].replace(['object', 'float64', 'int64']
                                                                                   ,['Character_Type','Numeric_Type','Numeric_Type'])
    return DataFrame_StaticInfo[['ColumnName', 'Dtype', 'NonNA_Rows', 'TotalRows', 'Saturation_Ratio']]


def function_GetNunique(para_DataFrame
                       ,para_DataFrame_StaticInfo = pd.DataFrame()
                       ,para_LowerLimit = 0.5):
    """
    @author:zhoujianjun
    @parameter: {para_DataFrame:输入数据框,para_DataFrame_StaticInfo:数据框的统计值,para_LowerLimit:最低饱和度}
    @create_date:
    @update_date:
    @purose:统计字符类型变量的个数，返回一个dataframe
    @commet:
    """
    # 调用非空统计函数
    DataFrame_StaticInfo = pd.DataFrame()
    if para_DataFrame_StaticInfo.empty == True:
        DataFrame_StaticInfo = function_GetDataFrameInfo(para_DataFrame)
    else:
        DataFrame_StaticInfo = para_DataFrame_StaticInfo

    # 过滤出满足最低饱和度的字符类型变量
    DataFrame_ChoiceColumn = DataFrame_StaticInfo[(DataFrame_StaticInfo.Dtype == 'Character_Type') & \
                                            (DataFrame_StaticInfo.Saturation_Ratio >= para_LowerLimit)]
    # 获取数据框每列有多少个唯一值
    list_Nunique = list(map(lambda str_Column
                                  :(str_Column + ',' + str(para_DataFrame[str_Column].nunique())).split(',')
                                  , list(DataFrame_ChoiceColumn.ColumnName)))
    
    DataFrame_Nunique = pd.DataFrame(list_Nunique, columns=['ColumnName', 'UniqueNum']) 
    DataFrame_Nunique['UniqueNum'] = DataFrame_Nunique['UniqueNum'].apply(int)
    return DataFrame_Nunique


def function_GetColumnName(para_DataFrame
                          ,para_Dtype
                          ,**kwargs):
    """
    @author:zhoujianjun
    @parameter: {para_DataFrame:输入数据框,para_Dtype:输入数据类型
                ,**kwargs 字典key值有Saturation_Ratio ：数据框的饱和度
                                    UniqueNum ：每个列唯一值的个数
                                    DeleteColumn ：要删除的列名   
                }
    @create_date:
    @update_date:
    @purose:获取想要的列名,返回一个filter类型变量
    @commet:
    """
    #获取饱和度的值
    Saturation_Ratio = 0
    if 'Saturation_Ratio' in kwargs.keys():
        Saturation_Ratio = kwargs['Saturation_Ratio']
    else:
        Saturation_Ratio = 0.5
    # 判断字符类型变量的
    bool_Uniquelimit = True
    if 'UniqueNum' in kwargs.keys():
        bool_Uniquelimit = (para_DataFrame.UniqueNum >= kwargs['UniqueNum'])
    else:
        bool_Uniquelimit = 1
    #判断要删除的列
    list_DeleteColumn = []
    if 'DeleteColumn' in kwargs.keys():
            list_DeleteColumn = kwargs['DeleteColumn']
    else:
        list_DeleteColumn = [] 
    #获取结果集
    DataFrame_Result = para_DataFrame[(para_DataFrame.Dtype == para_Dtype) & \
                                      (para_DataFrame.Saturation_Ratio >= Saturation_Ratio) & \
                                      (bool_Uniquelimit)]
    filter_Result = filter(lambda str_ColumnName :str_ColumnName not in list_DeleteColumn 
                                               ,list(DataFrame_Result['ColumnName'])) 
    return filter_Result

def function_GetCC(para_DataFrame
                  ,**kwargs):
    """
    @author:zhoujianjun
    @parameter: {para_DataFrame:输入数据框
                ,**kwargs 字典key值有CC_Method ：相关系数方法 有pearson,kendall,spearman 三个值，默认为 pearson
                                    CC_Ratio ：强相关系数比列 默认为0.6  
                }
    @create_date:
    @update_date:
    @purose:获取强相关系数
    @commet:
    """
    #获取动态函数参数
    CC_Method = ''
    if 'CC_Method' in kwargs.keys():
        CC_Method = kwargs['CC_Method']
    else:
        CC_Method = 'pearson'
    
    CC_Ratio = 0
    if 'CC_Ratio' in kwargs.keys():
        CC_Method = kwargs['CC_Ratio']
    else:
        CC_Ratio = 0.6
    
    DataFrame_CC = para_DataFrame.corr(method=CC_Method)


    # for int_index in range(len(list(DataFrame_CC.index))):
    #     for int_column in range(len(list(DataFrame_CC.columns))):
    #         if int_column >= int_index:
    #             DataFrame_CC.iloc[int_index, int_column] = 0
    list_Column = []
    list_Index = []
  
    for str_Column in list(DataFrame_CC.columns):
        for str_Index in list(DataFrame_CC.index):
            if (list(DataFrame_CC.index).index(str_Index) <= \
                list(DataFrame_CC.columns).index(str_Column)):
                DataFrame_CC.loc[str_Index,str_Column] = 0
        
        if (True in list(DataFrame_CC[str_Column] >= CC_Ratio)) & \
           (str_Column not in list_Column) & (str_Column not in list_Index):
            list_Column.append(str_Column)
        
        list_Index = list_Index + list(DataFrame_CC.index[DataFrame_CC[str_Column] >= CC_Ratio])

    return list_Column
