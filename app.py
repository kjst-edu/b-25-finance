from pathlib import Path
import pandas as pd
import plotly.express as px
from scipy import stats
from shiny import App, render, ui

# --- データ読み込み・前処理部分は変更なし ---
csv_file = Path(__file__).parent / "merged_result.csv"
df = pd.read_csv(csv_file, skiprows=4, na_values="***", thousands=r',')

csv_file2 = Path(__file__).parent / "FEI_PREF_260106110839.csv"
df2 = pd.read_csv(csv_file2, skiprows=4, na_values=["***", "X"], thousands=r',')

csv_file3 = Path(__file__).parent / "FEI_PREF_260113120951.csv"
df3 = pd.read_csv(csv_file3, skiprows=4, na_values=["***", "X"], thousands=r',')

base_cols = ["調査年", "地域"]
available_cols_df = [col for col in df.columns if any(x in col for x in ["総人口", "企業所得", "貸付金", "貸出金"])]
df = df[base_cols + available_cols_df]

available_cols_df2 = [col for col in df2.columns if "売上" in col or "C6301" in col]
df2 = df2[base_cols + available_cols_df2]

available_cols_df3 = [col for col in df3.columns if "就業者" in col or "完全失業者" in col or "F1102" in col or "F1107" in col]
df3 = df3[base_cols + available_cols_df3]

df['調査年'] = df['調査年'].astype(str).str.replace('年度', '', regex=False)
df2['調査年'] = df2['調査年'].astype(str).str.replace('年度', '', regex=False)
df3['調査年'] = df3['調査年'].astype(str).str.replace('年度', '', regex=False)
df['地域'] = df['地域'].astype(str)
df2['地域'] = df2['地域'].astype(str)
df3['地域'] = df3['地域'].astype(str)

df = df.merge(df2, on=['調査年', '地域'], how='left')
df = df.merge(df3, on=['調査年', '地域'], how='left')

# 産業別売上の集計
primary_cols = [col for col in df.columns if "農林漁業" in col or ("農業" in col and "林業" in col) or ("漁業" in col and "農林" not in col and "農業" not in col)]
if primary_cols: df["第一次産業売上"] = df[primary_cols].sum(axis=1)

secondary_cols = [col for col in df.columns if "鉱業" in col or "建設業" in col or "製造業" in col]
if secondary_cols: df["第二次産業売上"] = df[secondary_cols].sum(axis=1)

tertiary_col = next((col for col in df.columns if "サービス産業" in col or "C6301" in col), None)
if tertiary_col: df["第三次産業売上"] = df[tertiary_col]

available_years = sorted(df["調査年"].unique())

x_var_choices = {col: "総人口" if "総人口" in col else "企業所得" if "企業所得" in col else "貸出金" if "貸出金" in col else "貸付金" for col in df.columns if any(x in col for x in ["総人口", "企業所得", "貸出金", "貸付金"])}
y_var_choices = {col: "企業所得" if "企業所得" in col else "貸出金" if "貸出金" in col else "貸付金" if "貸付金" in col else "就業者数" if any(x in col for x in ["就業者", "F1102"]) else "完全失業者数" for col in df.columns if any(x in col for x in ["企業所得", "貸出金", "貸付金", "就業者", "F1102", "完全失業者", "F1107"])}

if "第一次産業売上" in df.columns: y_var_choices["第一次産業売上"] = "第一次産業売上"
if "第二次産業売上" in df.columns: y_var_choices["第二次産業売上"] = "第二次産業売上"
if "第三次産業売上" in df.columns: y_var_choices["第三次産業売上"] = "第三次産業売上"

x_default = list(x_var_choices.keys())[0] if x_var_choices else None
y_default = "第一次産業売上" if "第一次産業売上" in y_var_choices else list(y_var_choices.keys())[0]

# --- UI定義（ここを修正しました） ---
app_ui = ui.page_fluid(
    ui.panel_title("都道府県データ可視化"),
    
    ui.layout_sidebar(
        # 左側のサイドバー（項目欄）
        ui.sidebar(
            ui.input_selectize(
                "year", "調査年度を選択:",
                {year: year for year in available_years},
                selected="2020" if "2020" in available_years else available_years[0]
            ),
            ui.input_selectize("x_var", "X軸の変数を選択:", x_var_choices, selected=x_default),
            ui.input_selectize("y_var", "Y軸の変数を選択:", y_var_choices, selected=y_default),
            title="グラフ設定"
        ),
        
        # 右側のメインパネル（グラフ表示）
        ui.output_ui("scatter_plot"),
        ui.output_text("info")
    )
)

# サーバー定義
def server(input, output, session):
    @render.ui
    def scatter_plot():
        selected_year = input.year()
        df_filtered = df.query(f"調査年 == '{selected_year}'")
        
        x_var = input.x_var()
        y_var = input.y_var()
        
        temp_df = df_filtered[['地域', x_var, y_var]].copy()
        temp_df[x_var] = pd.to_numeric(temp_df[x_var], errors='coerce')
        temp_df[y_var] = pd.to_numeric(temp_df[y_var], errors='coerce')
        df_clean = temp_df.dropna()
        
        label_map = {**x_var_choices, **y_var_choices}
        x_label = label_map.get(x_var, x_var)
        y_label = label_map.get(y_var, y_var)
        
        corr_text = ""
        if len(df_clean) > 1:
            corr, p_value = stats.pearsonr(df_clean[x_var], df_clean[y_var])
            p_text = f"{p_value:.2e}" if p_value < 0.001 else f"{p_value:.4f}"
            corr_text = f"相関係数: {corr:.3f}, p値: {p_text}, n={len(df_clean)}"
        
        fig = px.scatter(
            df_clean, x=x_var, y=y_var,
            hover_data={'地域': True, x_var: ':.2f', y_var: ':.2f'},
            labels={x_var: x_label, y_var: y_label},
            title=f"{x_label}と{y_label}の相関 ({selected_year})<br><sub>{corr_text}</sub>"
        )
        
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         f'{x_label}: %{{x:,.2f}}<br>' +
                         f'{y_label}: %{{y:,.2f}}<extra></extra>',
            marker=dict(size=10, opacity=0.6)
        )
        
        fig.update_layout(
            autosize=True, # メインパネルの幅に合わせる
            height=600,
            hovermode='closest',
            font=dict(family="sans-serif"),
            margin=dict(l=20, r=20, t=60, b=20) # 余白の調整
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))
    
    @render.text
    def info():
        label_map = {**x_var_choices, **y_var_choices}
        x_label = label_map.get(input.x_var(), input.x_var())
        y_label = label_map.get(input.y_var(), input.y_var())
        return f"選択: 年度={input.year()}, X軸={x_label}, Y軸={y_label}"

app = App(app_ui, server)