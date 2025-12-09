import csv
import traceback # エラーの詳細を表示するための機能

input_file = 'nme_R031.4079267.20251125114943.01.csv'   # 元ファイル名
output_file = 'result.csv' # 出力ファイル名

# ★重要★ エラーが出る場合、ここを 'utf-8' から 'cp932' (または 'shift_jis') に変えてください
encoding_type = 'utf-8' 

print("処理を開始します...")

try:
    with open(input_file, 'r', encoding=encoding_type, newline='') as f_in, \
         open(output_file, 'w', encoding=encoding_type, newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        # 1. 最初の2行をスキップ（空読み）
        try:
            next(reader) # 1行目
            next(reader) # 2行目
        except StopIteration:
            print("エラー: ファイルの行数が足りません。")
            exit()

        count = 0
        # 2. 3行目以降を1行ずつ処理
        for i, row in enumerate(reader, start=3):
            # 空行（データがない行）はスキップ
            if not row:
                continue

            # 要素が足りない行（西暦しかないなど）をスキップしてエラー回避
            if len(row) < 2:
                print(f"警告: {i}行目のデータが不足しているためスキップしました: {row}")
                continue

            try:
                # 一番左（0番目）を「西暦」として取得
                year = row[0]
                
                # 残りのデータ（1番目以降）をすべて取得
                values = row[1:]

                # 縦に並べて書き込み
                for val in values:
                    writer.writerow([year, val])
                    count += 1
            except Exception as e:
                print(f"警告: {i}行目の処理中に問題が発生しました: {e}")

    print(f"完了しました！ {output_file} に {count} 件のデータを出力しました。")

except UnicodeDecodeError:
    print("\n【エラー: 文字コードが違います】")
    print(f"現在の設定は '{encoding_type}' です。")
    print("コード内の encoding_type = 'cp932' (または 'shift_jis') に書き換えて再実行してください。")
    
except FileNotFoundError:
    print(f"\n【エラー】ファイル '{input_file}' が見つかりません。")

except Exception as e:
    print("\n【予期せぬエラーの詳細】")
    # ここで本当のエラー原因を表示します
    traceback.print_exc()