import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # .envファイルを読み込み
client = OpenAI(api_key=os.getenv('API_KEY'))  #環境変数を取得
print(client.api_key)