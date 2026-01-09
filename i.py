from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

from shiny import App, render, ui

# データの読み込み
csv_file = Path(__file__).parent / "FEI_PREF_251111120136.csv"
df = pd.read_csv(csv_file, skiprows=4, na_values="***", thousands=r',')

# デバッグ: 列名を確認
print("元のCSVの列名:")
print(df.columns.tolist())

# 新しいCSVファイルの読み込み
csv_file2 = Path(__file__).parent / "FEI_PREF_260106110839.csv"
df2 = pd.read_csv(csv_file2, skiprows=4, na_values=["***", "X"], thousands=r',')

# デバッグ: 新しいCSVの列名を確認
print("\n新しいCSVの列名:")
print(df2.columns.tolist())

# 実際の列名を取得（最初の3列は調査年、地域関連として扱う）
base_cols = ["調査年", "地域"]

# df から必要な列を探す（総人口、企業所得、貸付金）
available_cols_df = [col for col in df.columns if any(x in col for x in ["総人口", "企業所得", "貸付金"])]
df_cols = base_cols + available_cols_df
df = df[df_cols]

# df2から売上関連の列を探す
available_cols_df2 = [col for col in df2.columns if "売上" in col or "C6301" in col]
df2_cols = base_cols + available_cols_df2
df2 = df2[df2_cols]

print("\ndf に含まれる列:", df.columns.tolist())
print("df2 に含まれる列:", df2.columns.tolist())

# データを結合
df = df.merge(df2, on=['調査年', '地域'], how='left')

# 産業別売上の集計列を作成
# 第一次産業売上 = 農林漁業 + 農業、林業 + 漁業
primary_cols = []
for col in df.columns:
    if "農林漁業" in col or ("農業" in col and "林業" in col) or ("漁業" in col and "農林" not in col and "農業" not in col):
        primary_cols.append(col)

if primary_cols:
    df["第一次産業売上"] = df[primary_cols].sum(axis=1)
    print(f"\n第一次産業売上を計算: {primary_cols}")

# 第二次産業売上 = 鉱業等 + 建設業 + 製造業
secondary_cols = []
for col in df.columns:
    if "鉱業" in col or "建設業" in col or "製造業" in col:
        secondary_cols.append(col)

if secondary_cols:
    df["第二次産業売上"] = df[secondary_cols].sum(axis=1)
    print(f"第二次産業売上を計算: {secondary_cols}")

# 第三次産業売上 = サービス産業
tertiary_col = None
for col in df.columns:
    if "サービス産業" in col or "C6301" in col:
        tertiary_col = col
        break

if tertiary_col:
    df["第三次産業売上"] = df[tertiary_col]
    print(f"第三次産業売上を設定: {tertiary_col}")

# result.csvの読み込みと処理
try:
    result_file = Path(__file__).parent / "result.csv"
    df_result = pd.read_csv(result_file, header=None, names=['年', '都道府県別貸出金'])
    
    # 都道府県リスト（47都道府県の順番）
    prefectures = [
        '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
        '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
        '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
        '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府',
        '兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県',
        '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県',
        '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
    ]
    
    # 都道府県名を繰り返しパターンで追加
    num_years = len(df_result) // 47
    df_result['地域'] = prefectures * num_years
    
    # 調査年を「1999年度」の形式に変換
    df_result['調査年'] = df_result['年'].astype(str) + '年度'
    
    # 必要な列のみ選択
    df_result = df_result[['調査年', '地域', '都道府県別貸出金']]
    
    # dfにマージ
    df = df.merge(df_result, on=['調査年', '地域'], how='left')
    
    print("✓ result.csvを正常に読み込み、統合しました")
    has_kashidashikin = True
    
except Exception as e:
    print(f"result.csv読み込みエラー: {e}")
    has_kashidashikin = False

# 利用可能な年度のリストを取得
available_years = sorted(df["調査年"].unique())

# X軸の変数の選択肢を動的に作成
x_var_choices = {}
for col in df.columns:
    if "総人口" in col:
        x_var_choices[col] = "総人口"
    elif "企業所得" in col:
        x_var_choices[col] = "企業所得"

if has_kashidashikin:
    x_var_choices["都道府県別貸出金"] = "都道府県別貸出金"

# Y軸の変数の選択肢を動的に作成（元のデータ + 新しい産業別売上）
y_var_choices = {}

# 企業所得のみ追加（総人口と貸付金は除外）
for col in df.columns:
    if "企業所得" in col:
        y_var_choices[col] = "企業所得"

if has_kashidashikin:
    y_var_choices["都道府県別貸出金"] = "都道府県別貸出金"

# 産業別売上を追加
if "第一次産業売上" in df.columns:
    y_var_choices["第一次産業売上"] = "第一次産業売上"
if "第二次産業売上" in df.columns:
    y_var_choices["第二次産業売上"] = "第二次産業売上"
if "第三次産業売上" in df.columns:
    y_var_choices["第三次産業売上"] = "第三次産業売上"

# デフォルトの選択を設定
x_default = list(x_var_choices.keys())[0] if x_var_choices else None
y_default = "第一次産業売上" if "第一次産業売上" in y_var_choices else list(y_var_choices.keys())[0]

# UI定義
app_ui = ui.page_fluid(
    ui.h2("都道府県データ可視化"),
    ui.input_selectize(  
        "year",  
        "調査年度を選択:",  
        {year: year for year in available_years},
        selected="2020年度" if "2020年度" in available_years else available_years[0]
    ),
    ui.input_selectize(  
        "x_var",  
        "X軸の変数を選択:",  
        x_var_choices,
        selected=x_default
    ),
    ui.input_selectize(  
        "y_var",  
        "Y軸の変数を選択:",  
        y_var_choices,
        selected=y_default
    ),
    ui.output_ui("scatter_plot"),
    ui.output_text("info")
)

# サーバー定義
def server(input, output, session):
    @render.ui
    def scatter_plot():
        # 選択された年度でフィルタリング
        selected_year = input.year()
        df_filtered = df.query(f"調査年 == '{selected_year}'")
        
        x_var = input.x_var()
        y_var = input.y_var()
        
        # 欠損値を除外（地域列も含める）
        df_clean = df_filtered[['地域', x_var, y_var]].dropna()
        
        # ラベル表示用の辞書（X軸とY軸を統合）
        label_map = {**x_var_choices, **y_var_choices}
        
        x_label = label_map.get(x_var, x_var)
        y_label = label_map.get(y_var, y_var)
        
        # 相関係数を計算
        corr_text = ""
        if len(df_clean) > 1:
            corr, p_value = stats.pearsonr(df_clean[x_var], df_clean[y_var])
            corr_text = f"相関係数: {corr:.3f}, p値: {p_value:.4f}"
        
        # Plotlyで散布図を作成
        fig = px.scatter(
            df_clean,
            x=x_var,
            y=y_var,
            hover_data={'地域': True, x_var: ':.2f', y_var: ':.2f'},
            labels={x_var: x_label, y_var: y_label},
            title=f"{x_label}と{y_label}の相関 ({selected_year})<br><sub>{corr_text}</sub>"
        )
        
        # ホバーテンプレートをカスタマイズ
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         f'{x_label}: %{{x:.2f}}<br>' +
                         f'{y_label}: %{{y:.2f}}<extra></extra>',
            marker=dict(size=10, opacity=0.6)
        )
        
        fig.update_layout(
            width=800,
            height=600,
            hovermode='closest',
            font=dict(family="sans-serif")
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
    
    @render.text
    def info():
        label_map = {**x_var_choices, **y_var_choices}
        x_label = label_map.get(input.x_var(), input.x_var())
        y_label = label_map.get(input.y_var(), input.y_var())
        return f"選択: 年度={input.year()}, X軸={x_label}, Y軸={y_label}"

app = App(app_ui, server)