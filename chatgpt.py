import os

import openai
from openai import OpenAI
from colorama import Fore
from dotenv import load_dotenv

EXIT_COMMAND = "exit()"
DEFAULT_MODEL = "gpt-4o-mini"

# .envファイルからAPIキーを取得
load_dotenv()  # .envファイルを読み込み
client = OpenAI(api_key=os.getenv('API_KEY'))


def give_role_to_system() -> str:
    """
    AIアシスタントに与える役割を入力させる
    :return: AIアシスタントに与える役割
    """

    # はじめの説明を表示
    print(f"\nAIアシスタントとチャットを始めます。チャットを終了させる場合は {EXIT_COMMAND} と入力してください。\n")

    # AIアシスタントに与える役割を入力
    system_role = input("AIアシスタントに与える役割がある場合は入力してください。\n"
                        "ない場合はそのままEnterキーを押してください。：")

    return system_role


def input_user_prompt() -> str:
    """
    ユーザーのプロンプトを入力させる
    :return: ユーザーのプロンプト
    """

    user_prompt = ""
    while not user_prompt:
        user_prompt = input(f"{Fore.CYAN}\nあなた：{Fore.RESET}")
        if not user_prompt:
            print("プロンプトを入力してください。")

    return user_prompt


def generate_chat_log(gpt_model: str) -> list[dict]:
    """
    チャットを開始して、チャットログを返す
    :param gpt_model: GPTモデルの名前
    :return: チャットログ
    """

    # チャットのログを保存するリスト
    chat_log: list[dict] = []

    # 役割がある場合はチャットログに追加
    system_role = give_role_to_system()
    if system_role:
        chat_log.append({"role":"system", "content":system_role})

    while True:
        prompt = input_user_prompt()
        if prompt == EXIT_COMMAND:
            break

        # チャットログにユーザーの入力を追加
        chat_log.append({"role":"user", "content": prompt})

        # AIの応答を取得
        response = client.chat.completions.create(model=gpt_model,
                                                  messages=chat_log,
                                                  stream=True)

        # ストリーミングでAIの応答を取得
        role, content = stream_and_concatenate_response(response)

        # チャットログにAIの応答を追加
        chat_log.append({"role": role, "content": content})

    return chat_log


def stream_and_concatenate_response(response) -> tuple[str, str]:
    """
    AIの応答をストリーミングで取得したものをチャンクで表示し、結合して返す
    :param response: OpenAI.chat.completions.create()の戻り値
    :return: AIの応答の文字列、AIの応答の役割
    """

    print(f"{Fore.GREEN}\nAIアシスタント： {Fore.RESET}", end="")
    content_list: list[str] = []
    role = ""
    for chunk in response:
        chunk_delta = chunk.choices[0].delta
        content_chunk = chunk_delta.content if chunk_delta.content is not None else ""
        role_chunk = chunk_delta.role
        if role_chunk:
            role = role_chunk
        content_list.append(content_chunk)
        print(content_chunk, end="")
    else:
        print()
        content = "".join(content_list)

    return role, content


def print_error_message(message: str):
    """
    エラーメッセージを表示する
    :param message: エラーメッセージ
    """

    print(f"{Fore.RED}{message}{Fore.RESET}")


def fetch_gpt_model_list() -> list[str] | None:
    """
    GPTモデルの一覧を取得
    :return: GPTモデルの一覧
    """

    # モデルの一覧の取得
    try:
        all_model_list = client.models.list()
    except openai.InternalServerError:
        print_error_message("OpenAI側でエラーが発生しています。少し待ってから再度試してください。")
        print("サービス稼働状況はhttps://status.openai.comで確認できます。")
    except openai.AuthenticationError:
        print_error_message("APIキーが正しく設定されていません。")
    except openai.APITimeoutError:
        print_error_message("APIのタイムアウトが発生しました。しばらくしてから再度実行してください。")
    except openai.RateLimitError:
        print_error_message("APIのレート制限に達しました。")
    except openai.APIError:
        print_error_message("エラーが発生しました。")
    else:
        # GPTモデルのみ抽出する
        gpt_model_list = []
        for model in all_model_list:
            if "gpt" in model.id:
                gpt_model_list.append(model.id)

        # モデル名でソート
        gpt_model_list.sort()

        return gpt_model_list


def choice_model(gpt_model_list: list[str]) -> str:
    """
    チャットで使うモデルを選択させる
    :param gpt_model_list: GPTモデルの一覧
    :return: 選択したモデル名
    """

    # モデルの一覧を表示
    print("AIとのチャットに使うモデルの番号を入力しEnterキーを押してください。")
    for num, model in enumerate(gpt_model_list):
        print(f"{num} : {model}")

    while True:
        input_number = input(f"何も入力しない場合は {DEFAULT_MODEL} を使います。：")

        # 何も入力されなかった場合
        if not input_number:
            return DEFAULT_MODEL

        # 数字じゃなかった場合
        if not input_number.isdigit():
            print_error_message("数字を入力してください。")

        # モデル一覧の範囲外の数字だった場合
        elif not int(input_number) in range(len(gpt_model_list)):
            print_error_message("その番号は選択肢に存在しません。")

        # 正常な入力だった場合
        else:
            user_choice_model_name = gpt_model_list[int(input_number)]
            return user_choice_model_name


def get_initial_prompt(chat_log: list[dict]) -> str | None:
    """
    チャットの履歴からユーザーの最初のプロンプトを取得する。
    :param chat_log: チャットの履歴
    :return: ユーザーの最初のプロンプト
    """

    # ユーザーの最初のプロンプトを取得
    for log in chat_log:
        if log["role"] == "user":
            initial_prompt = log["content"]
            return initial_prompt


def generate_summary(initial_prompt: str, summary_length: int=10) -> str:
    """
    ユーザーの最初のプロンプトを要約する。
    :param initial_prompt: ユーザーの最初のプロンプト
    :param summary_length: 要約する文字数の上限
    :return: 要約されたプロンプト
    """

    summary_request = {"role":"system",
                       "content":"あなたはユーザーの依頼を要約する役割を担います。"
                       f"以下のユーザーの依頼を必ず {summary_length} 文字以内で要約してください。"}

    # GPTによる要約を取得
    messages = [summary_request, {"role":"user", "content": initial_prompt}]
    response = client.chat.completions.create(model=DEFAULT_MODEL,
                                              messages=messages,
                                              max_tokens=summary_length)
    summary = response.choices[0].message.content
    adjustment_summary = summary[:summary_length]
    return adjustment_summary


def chat_runner() -> tuple[list[dict], str]:
    """
    チャットを開始し、チャットログとユーザーの最初のプロンプトを要約して返す。
    :return: チャットログ、ユーザーの最初のプロンプトの要約
    """

    # チャットを開始
    # GPTモデルの一覧を取得
    gpt_models = fetch_gpt_model_list()
    # モデル一覧が取得できなかったら終了
    if not gpt_models:
        exit()

    # チャットで使うモデルを選択
    choice = choice_model(gpt_models)
    # チャットログを取得
    generate_log = generate_chat_log(choice)
    # チャットログが空だったら終了
    if not generate_log:
        exit()

    # ユーザーの最初のプロンプトを取得
    initial_user_prompt = get_initial_prompt(generate_log)

    initial_prompt_summary = ""
    if initial_user_prompt:
        # ユーザーの最初のプロンプトを要約
        initial_prompt_summary = generate_summary(initial_user_prompt)

    return generate_log, initial_prompt_summary


if __name__ == "__main__":
    chat_runner()
