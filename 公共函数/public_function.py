import pandas as pd 
import io as io 
from functools import reduce

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
    # 获取行数
    TotalRows = para_DataFrame.shape[0]
    # 将数据框的每列的信息结果转为数据框格式
    str_Buffer = io.StringIO()
    para_DataFrame.info(null_counts=True
                       ,verbose=True
                       ,memory_usage='deep'
                       , buf=str_Buffer)
    list_Info = str_Buffer.getvalue().split('\n')[3:-3]
    list_StaticInfo = list(map(lambda str_Info
                                     :(str_Info.split(' ')[0] + ' ' + \
                                      str_Info.split(' ')[-3] + ' ' + \
                                      str_Info.split(' ')[-1]).split(' ')
                                     ,list_Info))
    DataFrame_StaticInfo = pd.DataFrame(list_StaticInfo
                                       ,columns=['ColumnName','Non_NA_Ratio','ColumnType'])
    # 获取每个列非空占比
    DataFrame_StaticInfo['Non_NA_Ratio'] = DataFrame_StaticInfo['Non_NA_Ratio'].apply(int) / TotalRows
    # 将字符类型做转换
    DataFrame_StaticInfo['ColumnType'] = DataFrame_StaticInfo['ColumnType'].replace(['object', 'float64', 'int64']
                                                                                   ,['Character_Type','Numeric_Type','Numeric_Type'])
    # 获取数据框每列有多少个唯一值
    list_Nunique = list(map(lambda str_Column
                                  :(str_Column + ',' + str(para_DataFrame[str_Column].nunique())).split(',')
                                  ,para_DataFrame.columns))
    
    DataFrame_Nunique = pd.DataFrame(list_Nunique, columns=['ColumnName', 'UniqueNum'])   
    # 两个数据框合并
    DataFrame_Result = function_MergeDataFrame('ColumnName'
                                             ,'left'
                                             ,DataFrame_StaticInfo
                                             ,DataFrame_Nunique)
    return DataFrame_Result