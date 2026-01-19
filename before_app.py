from pathlib import Path
import pandas as pd
import plotly.express as px
from scipy import stats
from shiny import App, render, ui

# データの読み込み
csv_file = Path(__file__).parent / "merged_result.csv"
df = pd.read_csv(csv_file, skiprows=4, na_values="***", thousands=r',')

# 新しいCSVファイルの読み込み
csv_file2 = Path(__file__).parent / "FEI_PREF_260106110839.csv"
df2 = pd.read_csv(csv_file2, skiprows=4, na_values=["***", "X"], thousands=r',')

# 3つ目のCSVファイルの読み込み（就業者数・完全失業者数）
csv_file3 = Path(__file__).parent / "FEI_PREF_260113120951.csv"
df3 = pd.read_csv(csv_file3, skiprows=4, na_values=["***", "X"], thousands=r',')

# 実際の列名を取得（最初の3列は調査年、地域関連として扱う）
base_cols = ["調査年", "地域"]

# df から必要な列を探す（総人口、企業所得、貸付金、貸出金）
# 修正済みのCSVならここで貸付金と貸出金が別々に取得されます
available_cols_df = [col for col in df.columns if any(x in col for x in ["総人口", "企業所得", "貸付金", "貸出金"])]
df_cols = base_cols + available_cols_df
df = df[df_cols]

# df2から売上関連の列を探す
available_cols_df2 = [col for col in df2.columns if "売上" in col or "C6301" in col]
df2_cols = base_cols + available_cols_df2
df2 = df2[df2_cols]

# df3から就業者数・完全失業者数の列を探す
available_cols_df3 = [col for col in df3.columns if "就業者" in col or "完全失業者" in col or "F1102" in col or "F1107" in col]
df3_cols = base_cols + available_cols_df3
df3 = df3[df3_cols]

# --- 結合前のデータ型統一（エラー対策） ---
# 調査年を文字列に統一し、「年度」を削除
df['調査年'] = df['調査年'].astype(str).str.replace('年度', '', regex=False)
df2['調査年'] = df2['調査年'].astype(str).str.replace('年度', '', regex=False)
df3['調査年'] = df3['調査年'].astype(str).str.replace('年度', '', regex=False)

# 地域も文字列に統一（数値や空欄による不一致を防ぐ）
df['地域'] = df['地域'].astype(str)
df2['地域'] = df2['地域'].astype(str)
df3['地域'] = df3['地域'].astype(str)
# ----------------------------------------

# データを結合
df = df.merge(df2, on=['調査年', '地域'], how='left')
df = df.merge(df3, on=['調査年', '地域'], how='left')

# 産業別売上の集計列を作成
# 第一次産業売上
primary_cols = []
for col in df.columns:
    if "農林漁業" in col or ("農業" in col and "林業" in col) or ("漁業" in col and "農林" not in col and "農業" not in col):
        primary_cols.append(col)
if primary_cols:
    df["第一次産業売上"] = df[primary_cols].sum(axis=1)

# 第二次産業売上
secondary_cols = []
for col in df.columns:
    if "鉱業" in col or "建設業" in col or "製造業" in col:
        secondary_cols.append(col)
if secondary_cols:
    df["第二次産業売上"] = df[secondary_cols].sum(axis=1)

# 第三次産業売上
tertiary_col = None
for col in df.columns:
    if "サービス産業" in col or "C6301" in col:
        tertiary_col = col
        break
if tertiary_col:
    df["第三次産業売上"] = df[tertiary_col]

# 利用可能な年度のリストを取得
available_years = sorted(df["調査年"].unique())

# --- X軸の変数の選択肢を動的に作成 ---
x_var_choices = {}
for col in df.columns:
    if "総人口" in col:
        x_var_choices[col] = "総人口"
    elif "企業所得" in col:
        x_var_choices[col] = "企業所得"
    elif "貸出金" in col:  # 貸出金を優先的にチェック
        x_var_choices[col] = "貸出金"
    elif "貸付金" in col:
        x_var_choices[col] = "貸付金"

# --- Y軸の変数の選択肢を動的に作成 ---
y_var_choices = {}
for col in df.columns:
    if "企業所得" in col:
        y_var_choices[col] = "企業所得"
    elif "貸出金" in col:
        y_var_choices[col] = "貸出金"
    elif "貸付金" in col:
        y_var_choices[col] = "貸付金"
    elif "就業者" in col or "F1102" in col:
        y_var_choices[col] = "就業者数"
    elif "完全失業者" in col or "F1107" in col:
        y_var_choices[col] = "完全失業者数"

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
        selected="2020" if "2020" in available_years else available_years[0]
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
        # 数値以外のデータが混ざっている場合に備えてcoerce変換してからdropna
        temp_df = df_filtered[['地域', x_var, y_var]].copy()
        temp_df[x_var] = pd.to_numeric(temp_df[x_var], errors='coerce')
        temp_df[y_var] = pd.to_numeric(temp_df[y_var], errors='coerce')
        df_clean = temp_df.dropna()
        
        # ラベル表示用の辞書（X軸とY軸を統合）
        label_map = {**x_var_choices, **y_var_choices}
        
        x_label = label_map.get(x_var, x_var)
        y_label = label_map.get(y_var, y_var)
        
        # 相関係数を計算
        corr_text = ""
        if len(df_clean) > 1:
            corr, p_value = stats.pearsonr(df_clean[x_var], df_clean[y_var])
            
            # p値を適切な形式で表示
            if p_value < 0.001:
                # 非常に小さい値は科学的記数法で表示
                p_text = f"{p_value:.2e}"
            else:
                # それ以外は通常の小数表記
                p_text = f"{p_value:.4f}"
            
            # サンプル数も表示
            corr_text = f"相関係数: {corr:.3f}, p値: {p_text}, n={len(df_clean)}"
        
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
                         f'{x_label}: %{{x:,.2f}}<br>' +
                         f'{y_label}: %{{y:,.2f}}<extra></extra>',
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