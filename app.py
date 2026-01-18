from pathlib import Path
import pandas as pd
import plotly.express as px
from scipy import stats
from shiny import App, render, ui

# =================================================================
# 1. データの準備
# =================================================================
csv_file = Path(__file__).parent / "merged_result.csv"
csv_file2 = Path(__file__).parent / "FEI_PREF_260106110839.csv"

# 読み込み
df = pd.read_csv(csv_file, skiprows=4, na_values="***", thousands=r',')
df2 = pd.read_csv(csv_file2, skiprows=4, na_values=["***", "X"], thousands=r',')

<<<<<<< HEAD
# 型変換
for d in [df, df2]:
    d['調査年'] = d['調査年'].astype(str).str.replace('年度', '', regex=False)
    d['地域'] = d['地域'].astype(str)

# 結合
=======
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
>>>>>>> b500ec7beb21f9e81dcc15b0a3595ef92e910c90
df = df.merge(df2, on=['調査年', '地域'], how='left')
df = df.merge(df3, on=['調査年', '地域'], how='left')

# 産業別売上の集計
p_cols = [c for c in df.columns if "農林漁業" in c or ("農業" in c and "林業" in c)]
if p_cols: df["第一次産業売上"] = df[p_cols].sum(axis=1)
s_cols = [c for c in df.columns if any(x in c for x in ["鉱業", "建設業", "製造業"])]
if s_cols: df["第二次産業売上"] = df[s_cols].sum(axis=1)
t_col = next((c for c in df.columns if "サービス産業" in c or "C6301" in c), None)
if t_col: df["第三次産業売上"] = df[t_col]

# 選択肢の作成
available_years = sorted(df["調査年"].unique())
x_var_choices = {c: "総人口" if "総人口" in c else "企業所得" if "企業所得" in c else "貸出金" if "貸出金" in c else "貸付金" for c in df.columns if any(x in c for x in ["総人口", "企業所得", "貸出金", "貸付金"])}
y_var_choices = {c: c.split('_')[-1] for c in df.columns if any(x in c for x in ["企業所得", "貸出金", "貸付金"])}
for cat in ["第一次産業売上", "第二次産業売上", "第三次産業売上"]:
    if cat in df.columns: y_var_choices[cat] = cat

# 「総人口」の列名を特定しておく（一人当たり計算用）
pop_col = next((k for k, v in x_var_choices.items() if v == "総人口"), None)

<<<<<<< HEAD
=======
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
>>>>>>> b500ec7beb21f9e81dcc15b0a3595ef92e910c90
x_default = list(x_var_choices.keys())[0] if x_var_choices else None
y_default = "第一次産業売上" if "第一次産業売上" in y_var_choices else list(y_var_choices.keys())[0]

# =================================================================
# 2. UIの定義
# =================================================================

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("分析設定", style="font-weight: bold;"),
        ui.hr(),
        ui.input_selectize("year", "調査年度:", {y: y for y in available_years}, 
                           selected="2020" if "2020" in available_years else available_years[0]),
        ui.hr(),
        ui.input_selectize("x_var", "X軸の変数:", x_var_choices, selected=x_default),
        ui.input_selectize("y_var", "Y軸の変数:", y_var_choices, selected=y_default),
        
        # --- 追加: 一人当たりモードのスイッチ ---
        ui.input_switch("per_capita", "一人当たり(人口比)で表示", value=False),
        ui.help_text("ONにすると、各指標を総人口で割った値を使用します。"),
        
        ui.hr(),
        ui.output_text("info"),
        width=320,
        open="always",
        id="sidebar_fixed"
    ),

    ui.tags.head(
        ui.tags.style("""
            .sidebar {
                border-right: 3px solid #495057 !important; 
                background-color: #f1f3f5 !important;
            }
            .bslib-page-sidebar {
                padding: 10px;
            }
        """)
    ),

    ui.card(
        ui.card_header("相関分析グラフ"),
        ui.output_ui("scatter_plot"),
        full_screen=True
    ),
    
    title="都道府県データ可視化ダッシュボード"
)

# =================================================================
# 3. サーバーロジック
# =================================================================

def server(input, output, session):
    @render.ui
    def scatter_plot():
        df_f = df.query(f"調査年 == '{input.year()}'").copy()
        xv, yv = input.x_var(), input.y_var()
        
        # 数値変換
        cols_to_fix = [xv, yv]
        if pop_col: cols_to_fix.append(pop_col)
        
        for c in set(cols_to_fix):
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce')
        
        # --- 一人当たり計算の実行 ---
        display_label_suffix = ""
        if input.per_capita() and pop_col:
            # 0除算を防ぐために、人口が0より大きい行のみ対象にする
            df_f = df_f[df_f[pop_col] > 0]
            df_f[xv] = df_f[xv] / df_f[pop_col]
            df_f[yv] = df_f[yv] / df_f[pop_col]
            display_label_suffix = " (一人当たり)"

        # クリーニング（欠損値削除）
        df_c = df_f[['地域', xv, yv]].dropna()
        
        # 相関係数
        corr_txt = ""
        if len(df_c) > 1:
            r, p = stats.pearsonr(df_c[xv], df_c[yv])
            corr_txt = f"相関係数: {r:.3f}, p値: {p:.4f}"
        
<<<<<<< HEAD
        # ラベルの準備
        x_label = x_var_choices.get(xv, xv) + display_label_suffix
        y_label = y_var_choices.get(yv, yv) + display_label_suffix
=======
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
>>>>>>> b500ec7beb21f9e81dcc15b0a3595ef92e910c90
        
        fig = px.scatter(
            df_c, x=xv, y=yv, hover_data=['地域'],
            labels={xv: x_label, yv: y_label},
            title=f"{x_label} vs {y_label}<br><sub>{corr_txt}</sub>"
        )
        
        # 一人当たりモードの時は軸のスケールが変わるため調整
        fig.update_layout(autosize=True, height=600, margin=dict(t=80))
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))
    
    @render.text
    def info():
        mode = "【一人当たりモード】" if input.per_capita() else "【通常モード】"
        return f"表示年度: {input.year()} / {mode}"

app = App(app_ui, server)