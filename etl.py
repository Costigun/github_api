import pandas as pd
import numpy as np

from sklearn import preprocessing

data['Product_Info_2_1'] = data['Product_Info_2'].str.slice(0,1)
data['Product_Info_2_2'] = pd.to_numeric(data['Product_Info_2'].str.slice(1,2))
data.drop('Product_Info_2',axis=1,inplace=True)
print(data.info())


# In[12]:


def reduce_mem_usage(df):
    start_mem = df.memory_usage().sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtypes
        if str(col_type)[:5] == 'float':
            c_min = df[col].min()
            c_max = df[col].max()
            if c_min > np.finfo('f2').min and c_max < np.finfo('f2').max:
                df[col] = df[col].astype(np.float16)
            elif c_min > np.finfo('f4').min and c_max < np.finfo('f4').max:
                df[col] = df[col].astype(np.float32)
            else:
                df[col] = df[col].astype(np.float64)
        elif str(col_type)[:3] == 'int':
            c_min = df[col].min()
            c_max = df[col].max()
            if c_min > np.iinfo('i1').min and c_max < np.iinfo('i1').max:
                df[col] = df[col].astype(np.int8)
            elif c_min > np.iinfo('i2').min and c_max < np.iinfo('i2').max:
                df[col] = df[col].astype(np.int16)
            elif c_min > np.iinfo('i4').min and c_max < np.iinfo('i4').max:
                df[col] = df[col].astype(np.int32)
            elif c_min > np.iinfo('i8').min and c_max < np.iinfo('i8').max:
                df[col] = df[col].astype(np.int64)
        else:
            df[col] = df[col].astype('category')
    end_mem = df.memory_usage().sum() / 1024 ** 2
    print(round(start_mem - end_mem,2))
    return df


# In[13]:


data = reduce_mem_usage(data)

for l in data['Product_Info_2_1'].unique():
    data['Product_Info_2_1' + l] = data['Product_Info_2_1'].isin([l]).astype('int8')
data.drop('Product_Info_2_1',axis=1,inplace=True)


# ### Заполним отсутствующие значения
# -1 увеличивает "расстояние" при расчете ближайших соседей

# In[16]:


data.fillna(-1,inplace=True)


# In[17]:


columns_groups = ['Insurance_History','Insured_Info','Medical_Keyword',
                  'Family_Hist','Medical_History','Product_Info']
columns = ['Wt','Ht','BMI','Ins_Age']

for cg in columns_groups:
    columns.extend(data.columns[data.columns.str.startswith(cg)])
print(columns)


# ### Предобработка данных
# Дополнительно проведем z-нормализацию данных через предварительную обработку (preprocessing). Нормализуем весь исходный набор данных.

# In[18]:


scaler = preprocessing.StandardScaler()
scaler.fit(pd.DataFrame(data,columns=columns))