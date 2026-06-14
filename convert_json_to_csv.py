# coding:utf-8
  
# Pandasをインポート
import pandas as pd
import json
import sys


def json_to_csv(path):
    # 変換したいJSONファイルを読み込む
    json_to_csv('test.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # JSONの構造に合わせて展開
        # 今回のデータ構造 {"data": [...]} に基づき、dataキーの中身を正規化
        df_json = pd.json_normalize(data['data'])

        output_file = "out.csv"
        df_json.to_csv(output_file, encoding='utf-8', index=False)
        print(df_json)
        print(f"\nSuccessfully converted {path} to {output_file}")

    except Exception as e:
         print(f"Error: {e}")

if __name__ == "__main__":
    target_file = "coffee_data.json"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]

    json_to_csv(target_file)
