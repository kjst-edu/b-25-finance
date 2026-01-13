import pandas as pd
import csv

# ファイル名
original_file = 'FEI_PREF_251111120136 copy.csv'
add_column_file = 'output.csv'

# 1. 元のファイルを「列数がバラバラでも読める方法」で読み込む
rows = []
try:
    # 統計データに多い Shift-JIS (cp932) で読み込み
    with open(original_file, 'r', encoding='cp932') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
except UnicodeDecodeError:
    # 失敗した場合は UTF-8 で読み込み
    with open(original_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

# リストからDataFrameに変換（これで列数が違っても自動的に調整されます）
df_orig = pd.DataFrame(rows)

# 2. 追加したいデータ（一列のデータ）を読み込む
df_add = pd.read_csv(add_column_file, header=None, encoding='utf-8-sig')

# 3. 追加するデータの開始位置を「6行目」に合わせる
# Pythonは0から数えるため、6行目はインデックス「5」になります
df_add.index = df_add.index + 5

# 4. 横方向に結合する（axis=1）
df_combined = pd.concat([df_orig, df_add], axis=1)

# 5. 書式変換：空白を "***" に、".0" を削除する
def final_format(x):
    # 値が空（None, NaN, 空文字）の場合
    if pd.isna(x) or str(x).strip() == "" or x is None:
        return "***"
    
    # すでに "***" になっているものはそのまま
    if x == "***":
        return "***"
    
    try:
        # 数値（132847.0など）から .0 を消す
        val = float(x)
        if val.is_integer():
            return str(int(val))
        else:
            return str(val)
    except (ValueError, TypeError):
        # 数値でない文字列はそのまま
        return str(x)

# 全データに適用
df_final = df_combined.applymap(final_format)

# 6. 結果をCSVファイルとして保存
df_final.to_csv('merged_result.csv', index=False, header=False, encoding='utf-8-sig')

print("結合が完了しました。'merged_result.csv' を作成しました。")