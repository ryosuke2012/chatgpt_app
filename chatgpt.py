import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # .envファイルを読み込み
client = OpenAI(api_key=os.getenv('API_KEY'))  #環境変数を取得
# はじめの説明を表示
print("AIアシスタントとチャットを始めます。チャットを終了させる場合はexit()と入力してください。")

# チャットのログを保存するリスト
chat_log: list[dict] = []

# todo AIに与える役割を入力

while True:
    prompt = input("あなた：")
    if prompt == "exit()":
        break

    # チャットログにユーザーの入力を追加
    chat_log.append({"role":"user", "content":prompt})

    # AIの応答を取得
    response = client.chat.completions.create(model="gpt-4o-mini", messages=chat_log)

    # AIの応答を表示
    content = response.choices[0].message.content

    # ロールを取得
    role = response.choices[0].message.role

    print(f"AI: {content}")

    chat_log.append({"role":role, "content":content})
