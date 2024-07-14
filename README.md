# Mare Demo

## デモ一覧
| id | デモ概要          | issue |  streamlit |
|----|------------------|-------|-------|
| 1  | GraphRAG     |   https://github.com/taku300/mare-demo/issues/1    |×|
| 2  | Insight AI     |   https://github.com/taku300/mare-demo/issues/2    |○|


## 環境構築
1. localでPythonが動く環境を用意
2. .envファイルを作成（.env_exampleを参照）
3. `pip install poetory`を依存関係を整理するためのpoetroyをインストール
4. `poetory insatll` でライブラリをインストール
5. `poetory shell`でそう環境の立ち上げ
6. `streamlit run src/app.py`でStreamlitを立ち上げ

※ Jupitorを立ち上げたい時は5まで実行したのちに`poetry run jupyter notebook`