# %%
from pathlib import Path
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

csv_file = Path(__file__).parent / "FEI_PREF_251111120136.csv"
df = pd.read_csv(csv_file, skiprows=4, na_values="***",
                 thousands=r',')
df = df[["調査年", 
         "地域", 
         "A1101_総人口【人】",
         "C1224_企業所得（平成27年基準）【百万円】",
         "D310412_貸付金（都道府県財政）【千円】",]]
         
df["A1101_総人口【人】"] = df["A1101_総人口【人】"].astype(int)
df["D310412_貸付金（都道府県財政）【千円】"] = df["D310412_貸付金（都道府県財政）【千円】"].astype(float)

df20 = df.query("調査年 == '2020年度'")

sns.relplot(df20, x="D310412_貸付金（都道府県財政）【千円】", y="C1224_企業所得（平成27年基準）【百万円】")

# %%