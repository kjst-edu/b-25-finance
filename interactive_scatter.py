import pandas as pd
import numpy as np
import plotly.express as px

# --- サンプルデータの準備 ---
np.random.seed(42)

# 100行のサンプルDataFrameを作成
# 各データポイントに表示したい詳細情報も列として追加
data = pd.DataFrame({
    '気温': np.random.normal(20, 5, 100),
    '湿度': np.random.normal(60, 10, 100),
    '売上': np.random.normal(100, 20, 100),
    '地域': np.random.choice(['東京', '大阪', '福岡', '札幌'], 100),
    '日付': pd.to_datetime('2023-01-01') + pd.to_timedelta(np.arange(100), unit='D'),
    '備考': [f'データポイント {i+1}' for i in range(100)]
})

# 「売上」と「気温」に相関を持たせる
data['売上'] = data['売上'] + (data['気温'] - 20) * 3

# -------------------------

# --- Plotly Express で散布図を作成 ---
# x軸: 気温, y軸: 売上
# hover_data にカーソルを合わせたときに表示したい詳細情報の列名をリストで指定します。
fig = px.scatter(
    data, 
    x="気温", 
    y="売上", 
    color="地域",  # 地域ごとに色分け
    size="湿度",   # 湿度によって点の大きさを変える
    hover_name="日付", # 太字で表示される項目 (必須ではないが便利)
    hover_data=["湿度", "地域", "備考", "日付"], # カーソルを合わせると表示される詳細情報
    title="気温と売上の関係 (インタラクティブ散布図)"
)

# グラフを表示
# これをJupyter NotebookやIDEで実行すると、インタラクティブなグラフがその場に表示されます。
# Pythonスクリプトとして実行した場合、ブラウザでグラフが開きます。
fig.show()

# HTMLファイルとして保存したい場合
# fig.write_html("interactive_scatterplot.html")