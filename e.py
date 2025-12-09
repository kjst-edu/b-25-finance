from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
from scipy import stats

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

# 変数の選択肢を動的に作成
var_choices = {
    "A1101_総人口【人】": "総人口",
    "C1224_企業所得（平成27年基準）【百万円】": "企業所得（平成27年基準）",
    "D310412_貸付金（都道府県財政）【千円】": "貸付金（都道府県財政）"
}

if has_kashidashikin:
    var_choices["都道府県別貸出金"] = "都道府県別貸出金"

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
        var_choices,
        selected="D310412_貸付金（都道府県財政）【千円】"
    ),
    ui.input_selectize(  
        "y_var",  
        "Y軸の変数を選択:",  
        var_choices,
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
        
        # 選択された年度でフィルタリング
        selected_year = input.year()
        df_filtered = df.query(f"調査年 == '{selected_year}'")
        
        x_var = input.x_var()
        y_var = input.y_var()
        
        # 欠損値を除外
        df_clean = df_filtered[[x_var, y_var]].dropna()
        
        # 散布図を作成
        sns.scatterplot(data=df_clean, x=x_var, y=y_var, s=100, alpha=0.6, ax=ax)
        
        # 相関係数を計算
        if len(df_clean) > 1:
            corr, p_value = stats.pearsonr(df_clean[x_var], df_clean[y_var])
            
            # 相関係数をグラフに表示
            ax.text(0.05, 0.95, f'相関係数: {corr:.3f}\np値: {p_value:.4f}',
                   transform=ax.transAxes,
                   fontsize=11,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # ラベル表示用の辞書
        label_map = {
            "A1101_総人口【人】": "総人口",
            "C1224_企業所得（平成27年基準）【百万円】": "企業所得",
            "D310412_貸付金（都道府県財政）【千円】": "貸付金（都道府県財政）",
            "都道府県別貸出金": "都道府県別貸出金"
        }
        
        x_label = label_map.get(x_var, x_var)
        y_label = label_map.get(y_var, y_var)
        
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_title(f"{x_label} vs {y_label} ({selected_year})", fontsize=14)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @render.text
    def info():
        x_label = var_choices.get(input.x_var(), input.x_var())
        y_label = var_choices.get(input.y_var(), input.y_var())
        return f"選択: 年度={input.year()}, X軸={x_label}, Y軸={y_label}"

app = App(app_ui, server)