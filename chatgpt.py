import os

from dotenv import load_dotenv
from httpx import stream
from openai import OpenAI

def chat_runner():
    """"チャットする関数"""

    # はじめの説明を表示
    print("AIアシスタントとチャットを始めます。チャットを終了させる場合はexit()と入力してください。\n")

    # チャットのログを保存するリスト
    chat_log: list[dict] = []

    # AIに与える役割を入力
    system_role = input("AIアシスタントに与える役割がある場合は入力してください。\n"
                        "ない場合はそのままEnterキーを押してください。：")
    if system_role:
        chat_log.append({"role":"system", "content":system_role})

    while True:
        prompt = input("あなた：")
        if prompt == "exit()":
            break

        # チャットログにユーザーの入力を追加
        chat_log.append({"role":"user", "content":prompt})

        # AIの応答を取得
        response = client.chat.completions.create(model="gpt-4o-mini", messages=chat_log, stream=True)

        print("AIアシスタント： ", end="")
        content = []
        role = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            content_chunk = delta.content if delta.content is not None else ""
            role_chunk = delta.role
            if role_chunk:
                role = role_chunk
            if content_chunk:
                content.append(content_chunk)
            print(content_chunk, end="")
        else:
            print()
            content = "".join(content)

        chat_log.append({"role":role, "content":content})

load_dotenv()  # .envファイルを読み込み
client = OpenAI(api_key=os.getenv('API_KEY'))
chat_runner()
