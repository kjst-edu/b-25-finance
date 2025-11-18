from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

from shiny import App, render, ui

# データの読み込み
csv_file = Path(__file__).parent / "FEI_PREF_251111120136.csv"
df = pd.read_csv(csv_file, skiprows=4, na_values="***", thousands=r',')
df = df[["調査年", 
         "地域", 
         "A1101_総人口【人】",
         "C1224_企業所得（平成27年基準）【百万円】",
         "D310412_貸付金（都道府県財政）【千円】"]]
         
df["A1101_総人口【人】"] = df["A1101_総人口【人】"].astype(int)
df["D310412_貸付金（都道府県財政）【千円】"] = df["D310412_貸付金（都道府県財政）【千円】"].astype(float)

# 利用可能な年度のリストを取得
available_years = sorted(df["調査年"].unique())

# UI定義
app_ui = ui.page_fluid(
    ui.h2("都道府県データ可視化"),
    ui.input_selectize(  
        "year",  
        "調査年度を選択:",  
        {year: year for year in available_years},
        selected="2020年度"
    ),
    ui.input_selectize(  
        "x_var",  
        "X軸の変数を選択:",  
        {
            "D310412_貸付金（都道府県財政）【千円】": "貸付金（都道府県財政）",
            "C1224_企業所得（平成27年基準）【百万円】": "企業所得（平成27年基準）",
            "A1101_総人口【人】": "総人口"
        },
        selected="D310412_貸付金（都道府県財政）【千円】"
    ),
    ui.input_selectize(  
        "y_var",  
        "Y軸の変数を選択:",  
        {
            "C1224_企業所得（平成27年基準）【百万円】": "企業所得（平成27年基準）",
            "D310412_貸付金（都道府県財政）【千円】": "貸付金（都道府県財政）",
            "A1101_総人口【人】": "総人口"
        },
        selected="C1224_企業所得（平成27年基準）【百万円】"
    ),
    ui.output_plot("scatter_plot", width="800px", height="600px"),
    ui.output_text("info")
)

# サーバー定義
def server(input, output, session):
    @render.plot
    def scatter_plot():
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 選択された年度でフィルタリング
        selected_year = input.year()
        df_filtered = df.query(f"調査年 == '{selected_year}'")
        
        x_var = input.x_var()
        y_var = input.y_var()
        
        # 散布図を作成
        scatter = ax.scatter(df_filtered[x_var], df_filtered[y_var], 
                            s=100, alpha=0.6)
        
        ax.set_xlabel(x_var, fontsize=12)
        ax.set_ylabel(y_var, fontsize=12)
        ax.set_title(f"{x_var} vs {y_var} ({selected_year})", fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # ホバー時に都道府県名を表示する機能
        annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                           bbox=dict(boxstyle="round", fc="w", alpha=0.8),
                           arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        
        def update_annot(ind):
            pos = scatter.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = df_filtered.iloc[ind["ind"][0]]["地域"]
            annot.set_text(text)
        
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = scatter.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect("motion_notify_event", hover)
        
        plt.tight_layout()
        return fig
    
    @render.text
    def info():
        return f"選択: 年度={input.year()}, X軸={input.x_var()}, Y軸={input.y_var()}"

app = App(app_ui, server)