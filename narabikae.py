import pandas as pd
import csv

# ファイル名
file_path = 'nme_R031.702729.20260113024255.01.csv'

try:
    # 1. 最初の2行をスキップして読み込む
    df = pd.read_csv(file_path, skiprows=2, header=None, encoding='cp932')
except UnicodeDecodeError:
    df = pd.read_csv(file_path, skiprows=2, header=None, encoding='utf-8')

# 2. 1列目（年度）を除外する
df_values_only = df.iloc[:, 1:]

# 3. 行の上下を逆転させる（最新年度を一番上に）
df_reversed = df_values_only.iloc[::-1]

# 4. データを1次元（1列）に変換
flattened_data = df_reversed.values.flatten()

# 5. 書式変換（.0の削除、および空データの「***」置換）
def format_clean(x):
    # 値が NaN（欠損値）または空文字の場合に "***" を返す
    if pd.isna(x) or str(x).strip() == "":
        return "***"
    
    try:
        # 数値（float）で、かつ中身が整数であれば整数に変換して .0 を消す
        val = float(x)
        if val.is_integer():
            return str(int(val))
        else:
            return str(val)
    except (ValueError, TypeError):
        # 数値でない場合はそのまま文字列で返す
        return str(x)

# 全データに適用
cleaned_data = [format_clean(v) for v in flattened_data]

# 6. 結果をCSVファイルとして保存
result_series = pd.Series(cleaned_data)
result_series.to_csv('output.csv', index=False, header=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)

print("空白を '***' に置換し、小数点を整理した 'output.csv' を作成しました。")