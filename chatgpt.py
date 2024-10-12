import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # .envファイルを読み込み
client = OpenAI(api_key=os.getenv('API_KEY'))  #環境変数を取得

# はじめの説明を表示
print("AIアシスタントとチャットを始めます。チャットを終了させる場合はexit()と入力してください。")

# チャットのログを保存するリスト
chat_log: list[dict] = []

while True:
    prompt = input("プロンプトを入力してください：")
    if prompt == "exit()":
        break

    # チャットログにユーザーの入力を追加
    chat_log.append({"role":"user", "content":prompt})

    # AIの応答を取得
    response = client.chat.completions.create(model="gpt-4o-mini", messages=chat_log)

    # AIの応答を表示
    print("AI:", response.model_dump_json(indent=2))
