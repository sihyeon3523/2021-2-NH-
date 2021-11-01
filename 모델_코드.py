# -*- coding: utf-8 -*-
"""민트맛보라_예선 제출 - 코드.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_sFZmiFzo4LEkBQv4ejWZSetpz7fWixG
"""

pip list

"""## 개발 환경(OS) 및 라이브러리 버전 
- 운영체제(os) Windows10
- pandas                             0.23.4           
- matplotlib                         3.1.3   
- numpy                              1.18.1   
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import KNNImputer
import numpy as np

df_cus = pd.read_csv("/data/cus_info.csv")

df_cus.head()

df_cus = df_cus.rename({'act_id':'계좌ID', 'sex_dit_cd':'성별', 'cus_age_stn_cd':'연령대',
               'ivs_icn_cd' : '투자성향', 'cus_aet_stn_cd': '자산구간', 
               'mrz_pdt_tp_sgm_cd': '주거래상품군','lsg_sgm_cd':'lifestage',
               'tco_cus_grd_cd':'서비스등급','tot_ivs_te_sgm_cd': '총투자기간',
              'mrz_btp_dit_cd': '주거래업종구분'}, axis = 1)

df_cus.head()

"""### 고객 데이터 결측값"""

df_cus['투자성향'].unique()

print('투자성향 결측치 : ', end= '')
print(len(df_cus[df_cus['투자성향'] == 99]) / len(df_cus)*100)
print('서비스등급 결측치 : ', end= '')
print(len(df_cus[df_cus['서비스등급'] == 99]) / len(df_cus)*100)

len(df_cus[df_cus['투자성향'] == 99].index)

len(df_cus[df_cus['서비스등급'] == 99].index)

len(df_cus)

"""### 주식 종복에 대한 코드 정보 결측값
- 시가총액 규모유형
- 시장구분
"""

df_iem = pd.read_csv("/data/iem_info.csv")

df_iem = df_iem.rename({'iem_cd': '종목코드', 'iem_krl_nm': '종목한글명','btp_cfc_cd' : '종목업종',
              'mkt_pr_tal_scl_tp_cd': '시가총액규모유형','stk_dit_cd':'시장구분'}, axis=1)

df_iem.head(3)

df_iem.shape

print('시가총액규모유형 : ', end = '')
print(len(df_iem[df_iem['시가총액규모유형'] == 99])/len(df_iem)*100, end = '')
print('%')
print('시장구분 : ', end = '')
print(len(df_iem[df_iem['시장구분'] == 99])/len(df_iem)*100, end = '')
print('%')

"""### 종합
- 투자성향 : 대체 
- 서비스등급 : 결측치 처리 안함 
- 시가총액규모유형 : 대체 
- 시장구분 : drop 
"""

print('투자성향 결측치 : ' + str(len(df_cus[df_cus['투자성향'] == 99]) / len(df_cus)*100) + '%')
print('서비스등급 결측치 : ' + str(len(df_cus[df_cus['서비스등급'] == 99]) / len(df_cus)*100) + '%')

print('시가총액규모유형 : ' + str(len(df_iem[df_iem['시가총액규모유형'] == 99])/len(df_iem)*100)+ '%')
print('시장구분 : ' + str(len(df_iem[df_iem['시장구분'] == 99])/len(df_iem)*100)+ '%')

"""### 결측값 처리 
- 행을 지우는 건 지양 : 계좌id가 없어질 수 있음 
- 시가총액규모유형 : 유가증권시장의 경우 6월부터 8월 마지막 영업일까지 하루평균 시가총액 순서로 1~100위는 대형주, 101~300위는 중형주, 그 외는 소형주로 분류. 코스닥시장은 중형주 기준이 101~400위. / 유가증권시장(코스피), 코스닥
- 코스피에서 시가총액 순위를 기준으로 만든 대형주, 중형주, 소형주 지수가 있음, 대형주 시가총액 1~100위, 시가총액 101 ~ 300위, 시가총액 301 ~ 
"""

# 시장구분 열 drop 
df_iem = df_iem.drop('시장구분', axis = 1)

# 투자성향 분포 확인 
df_cus['투자성향'].value_counts()

"""#### 시가총액규모유형 전처리 방법 
- 행을 지우는 건 지양 : 주식중목코드가 없어질 수 있음
- KODEX|TIGER|KINDEX|KTOP|KBSTAR|ARIRANG|HANARO|KOSEF 은 파생상품 혹은 펀드이므로, 새로운 라벨 "4" 추가. 
- ~우 인 데이터도 있음.. 05. 우량주 추가 
- 01: 대형주, 02: 중형주, 03: 소형주, 04: 파생상품, 05. 우량주, 99: 기타 
"""

# 시가총액규모유형 분포 확인 
df_iem['시가총액규모유형'].value_counts()

df_iem_null = df_iem[df_iem['시가총액규모유형'] == 99]

df_iem_null.to_csv("시가총액규모유형_결측치.csv", index = False)

# https://zephyrus1111.tistory.com/46
df_iem.query('종목한글명.str.contains("KODEX|TIGER|KINDEX|KTOP|KBSTAR|ARIRANG|HANARO|KOSEF")', engine='python')['시가총액규모유형'].replace(99,4, inplace = True)

# https://zephyrus1111.tistory.com/46
index_04 = df_iem.query('종목한글명.str.contains("KODEX|TIGER|KINDEX|KTOP|KBSTAR|ARIRANG|HANARO|KOSEF")', engine='python')['시가총액규모유형'].index

# 04 파생상품 추가 
for i in index_04: 
    df_iem.iloc[i, -1] = 4
    #print(df_iem.iloc[i, -1])

df_iem['시가총액규모유형'].value_counts()

index_05 = []
for i in range(len(df_iem)):
    if df_iem.loc[i, '종목한글명'].endswith('우'):
        index_05.append(i)

for i in index_05:
    df_iem.iloc[i, -1] = 5
    #print(df_iem.loc[i, '종목한글명'])

df_iem['시가총액규모유형'].value_counts()

df_iem.to_csv("iem_info_missingvalue_out.csv", index = False)

df_iem.shape

df_iem[df_iem['시가총액규모유형'] == 4]

df_iem[df_iem['시가총액규모유형'] == 5]

"""#### 투자성향 전처리 방법
- knn 으로 99에 해당하는 값 3687개 중에서 1000개만 99로 남김 (99에 대한 학습도 필요하니깐)
- 나머지 값은 null값으로 만듬
- knn 으로 n=3일때의 예측값 대치
- 35, 36 등과 같이 범주형 변수가 아닌 경우, 99로 바꿈
"""

df_cus = pd.read_csv("/data/cus_info.csv")

df_cus.head()

df_cus = df_cus.rename({'act_id':'계좌ID', 'sex_dit_cd':'성별', 'cus_age_stn_cd':'연령대',
               'ivs_icn_cd' : '투자성향', 'cus_aet_stn_cd': '자산구간', 
               'mrz_pdt_tp_sgm_cd': '주거래상품군','lsg_sgm_cd':'lifestage',
               'tco_cus_grd_cd':'서비스등급','tot_ivs_te_sgm_cd': '총투자기간',
              'mrz_btp_dit_cd': '주거래업종구분'}, axis = 1)

df_cus['투자성향'].replace({99, '99'}, inplace = True)

df_cus['투자성향'] = df_cus['투자성향'].astype('str')

type(df_cus['투자성향'][3])

df_cus_null = df_cus.copy()

type(df_cus_null['투자성향'][3])

index_null = df_cus_null[df_cus_null['투자성향'] == '99'][:-1000].index

len(index_null)

for i in index_null:
    df_cus_null.iloc[i, 3] = np.nan

df_cus_null.info()

# https://www.analyticsvidhya.com/blog/2020/07/knnimputer-a-robust-way-to-impute-missing-values-using-scikit-learn/
imputer = KNNImputer(n_neighbors = 3)

imputed = imputer.fit_transform(df_cus_null.iloc[:, 1:])

df_imputer = pd.DataFrame(imputed, columns = df_cus_null.columns[1:])

df_imputer['투자성향'].value_counts()

df_imputer['투자성향'] = df_imputer['투자성향'].astype('int')
df_imputer['성별'] = df_imputer['성별'].astype('int')
df_imputer['연령대'] = df_imputer['연령대'].astype('int')
df_imputer['자산구간'] = df_imputer['자산구간'].astype('int')
df_imputer['주거래상품군'] = df_imputer['주거래상품군'].astype('int')
df_imputer['lifestage'] = df_imputer['lifestage'].astype('int')
df_imputer['서비스등급'] = df_imputer['서비스등급'].astype('int')
df_imputer['총투자기간'] = df_imputer['총투자기간'].astype('int')
df_imputer['주거래업종구분'] = df_imputer['주거래업종구분'].astype('int')

df_imputer['투자성향'].value_counts()

df_imputer['투자성향'].replace(35, 99, inplace=True)
df_imputer['투자성향'].replace(34, 99, inplace=True)
df_imputer['투자성향'].replace(67, 99, inplace=True)
df_imputer['투자성향'].replace(36, 99, inplace=True)
df_imputer['투자성향'].replace(33, 99, inplace=True)
df_imputer['투자성향'].replace(66, 99, inplace=True)

df_imputer['투자성향'].value_counts()

df_imputer.info()

df_imputer_ver2 = pd.concat([df_cus_null['계좌ID'], df_imputer], axis = 1)

df_imputer_ver2.info()

df_imputer_ver2

df_imputer_ver2.to_csv("cus_info_missingvalue_out.csv", index= False)

"""### Baseline 모델로 모델 돌리기 """

import pandas as pd
pd.set_option("display.max_row", 100)
pd.set_option("display.max_column", 100)
import numpy as np
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
from lightgbm import LGBMRegressor

cus = pd.read_csv("/data/cus_info_missingvalue_out.csv")
iem = pd.read_csv("/data/iem_info_missingvalue_out.csv")
hist = pd.read_csv("/data/stk_bnc_hist.csv")
train = pd.read_csv("/data/stk_hld_train.csv")
test = pd.read_csv("/data/stk_hld_test.csv")

submission = pd.read_csv("/data/sample_submission.csv")

cus = cus.rename({'계좌ID':'act_id','성별':'sex_dit_cd','연령대':'cus_age_stn_cd',
                '투자성향':'ivs_icn_cd', '자산구간':'cus_aet_stn_cd', 
               '주거래상품군':'mrz_pdt_tp_sgm_cd','lifestage':'lsg_sgm_cd',
               '서비스등급':'tco_cus_grd_cd','총투자기간':'tot_ivs_te_sgm_cd',
              '주거래업종구분':'mrz_btp_dit_cd'}, axis = 1)

iem = iem.rename({'종목코드':'iem_cd','종목한글명':'iem_krl_nm', '종목업종': 'btp_cfc_cd',
              '시가총액규모유형':'mkt_pr_tal_scl_tp_cd','시장구분':'stk_dit_cd'}, axis=1)

iem.columns

iem

cus.columns

test



# 앞서 언급한 것처럼 베이스라인에서는 "hist_d" column을 임의로 생성하여 모델을 학습시키도록 하겠습니다.
# 베이스라인에서는 "hold_d"값, 즉 주식 보유기간의 0.6배에 해당하는 기간을 임의로 설정하여 "hist_d"를 생성하였습니다.
# 결국 모델은 "hist_d"만큼 주식을 보유 했을때의 "hold_d"를 예측하게 될 것입니다.

train["hist_d"] = train["hold_d"]*0.6
train.hist_d = np.trunc(train["hist_d"])

train.head(3)

# train과 test에 고객정보(cus_info)와 주식정보(iem_info)를 추가하겠습니다.

train_data = pd.merge(train, cus, how = "left", on = ["act_id"])
train_data = pd.merge(train_data, iem, how = "left", on = ["iem_cd"])

test_data = pd.merge(test, cus, how = "left", on = ["act_id"])
test_data = pd.merge(test_data, iem, how = "left", on = ["iem_cd"])

train_data.head(3)

# train_data에서 Y값을 추출한 후 hold_d column을 지워주겠습니다.

train_label = train_data["hold_d"]
train_data.drop(["hold_d"], axis = 1, inplace = True)

# 추가적으로 약간의 전처리를 통해 train data와 test data를 구성하겠습니다.

hist["stk_p"] = hist["tot_aet_amt"] / hist["bnc_qty"]
hist = hist.fillna(0)

train_data = pd.merge(train_data, hist, how = "left", on = ["act_id", "iem_cd"])
train_data = train_data[(train_data["byn_dt"] == train_data["bse_dt"])]
train_data.reset_index(drop = True, inplace = True)

test_data = pd.merge(test_data, hist, how = "left", on = ["act_id", "iem_cd"])
test_data = test_data[(test_data["byn_dt"] == test_data["bse_dt"])]
test_data.reset_index(drop = True, inplace = True)

train_data = train_data.drop(["act_id", "iem_cd", "byn_dt", "bse_dt"], axis = 1)
test_data = test_data.drop(["act_id", "iem_cd", "byn_dt", "submit_id", "hold_d", "bse_dt"], axis = 1)

L_encoder = LabelEncoder()
L_encoder.fit(iem["iem_krl_nm"])
train_data["iem_krl_nm"] = L_encoder.transform(train_data["iem_krl_nm"])
test_data["iem_krl_nm"] = L_encoder.transform(test_data["iem_krl_nm"])

train_data.head(3)

test_data.head(3)

train_data.reset_index(drop = True, inplace=True)
train_label.reset_index(drop = True, inplace=True)

models = []

folds = KFold(n_splits=10)
for train_idx, val_idx in folds.split(train_data):
    
    train_x = train_data.iloc[train_idx, :]
    train_y = train_label[train_idx]
    val_x = train_data.iloc[val_idx, :]
    val_y = train_label[val_idx]
    
    model = LGBMRegressor(objective= "regression",
                          max_depth= 8,
                          n_estimators= 2000,
                          learning_rate= 0.01,
                          num_leaves = 31)
    
    model.fit(train_x, train_y,
              eval_set=[(val_x, val_y)],
              eval_metric=["rmse"],
              early_stopping_rounds=300,
              verbose=500)
    
    models.append(model)

result = []
for i in models:
    result.append(i.predict(test_data))
predict = np.mean(result, axis = 0)

predict[:20]

submission["hold_d"] = np.round(predict)

submission.to_csv("dacon_baseline_missinvalue_ver2.csv", index = False)

