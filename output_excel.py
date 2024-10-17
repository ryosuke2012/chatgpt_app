import os
import subprocess
from pathlib import Path

import openpyxl

base_dir = Path(__file__).parent
excel_path = base_dir / 'chat_log.xlsx'

def is_output_open_excel() -> bool:
    """
    Excelファイルが開かれているかどうかを判定する
    :return: 開かれているかの真偽値
    """

    # Windows
    if os.name == "nt":
        try:
            with excel_path,open("r+b"):
                return False
        except PermissionError:
            return True
        except FileNotFoundError:
            return False

    # Mac
    if os.name == "posix":
        if excel_path.exists():
            result = subprocess.run(["lsof", excel_path], stdout=subprocess.PIPE)
            return bool(result.stdout)
        return False

def load_or_create_workbook():
    """
    Excelファイルを読み込むか、存在しない場合は作成する
    :return: ワークブックオブジェクトと、ファイルが作成されたかどうかのフラグ
    """

    # ファイルの存在確認
    if excel_path.exists():
        # ファイルを読み込んで返す
        pass
    else:
        # ファイルを作成して返す
        wb = openpyxl.Workbook()
        return wb

is_output = is_output_open_excel()
print(is_output)

workbook = load_or_create_workbook()
workbook.save(excel_path)
