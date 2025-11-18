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

df20 = df.query("調査年 == '2020年度'")

# UI定義
app_ui = ui.page_fluid(
    ui.h2("都道府県データ可視化"),
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
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_var = input.x_var()
        y_var = input.y_var()
        
        # 散布図を作成
        sns.scatterplot(data=df20, x=x_var, y=y_var, s=100, alpha=0.6, ax=ax)
        
        ax.set_xlabel(x_var, fontsize=12)
        ax.set_ylabel(y_var, fontsize=12)
        ax.set_title(f"{x_var} vs {y_var} (2020年度)", fontsize=14)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @render.text
    def info():
        return f"選択: X軸={input.x_var()}, Y軸={input.y_var()}"

app = App(app_ui, server)