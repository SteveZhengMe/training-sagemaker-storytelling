import argparse
import os
import sys
import datetime
import random

# KW: 不要在这里导入其他模块，因为它们可能会在prepare_env中被安装


def prepare_env(source_dir: str) -> None:
    """
    Add libraries in the requirements.txt file to the runtime environment.
    Add all .py in this folder to the runtime environment.
    """
    # KW: 把上传的目录作为Python运行时环境
    sys.path.append(source_dir)

    # 运行requirements.txt
    requirements_file = os.path.join(source_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        with open(requirements_file, "r") as f:
            for line in f:
                package = line.strip()
                if package and not package.startswith("#"):
                    # KW: Image中可能没有安装pip，所以不要使用pip install {package}，而要用python -m pip方式
                    os.system(f"{sys.executable} -m pip install {package}")


def pass_data(source_csv_name: str) -> str:
    # read csv file and the first line is the header and rest are data. header is a [], data is [[],[],...]
    with open(f"{source_csv_name}", "r") as f:
        lines = f.readlines()
        header = lines[0].strip().split(",")
        data = [line.strip().split(",") for line in lines[1:]]

        # KW: 在此处导入
        from processing_func import get_markdown_content

        return get_markdown_content(header, data)


def save_data(content: str, output_file: str) -> None:
    """
    Save the content to a file.
    """
    with open(output_file, "w") as f:
        f.write(content)


if __name__ == "__main__":
    """
    Parameters:
    - input_csv
    - output_result
    - source_dir
    """
    parser = argparse.ArgumentParser()
    # KW: 也可以在此处只传入文件名，在processing.py中拼接路径，因为数据总是在ml/input/和ml/output/目录下
    parser.add_argument(
        "--input_csv",
        type=str,
        required=True,
        help="Input source csv file path & name (e.g., ml/input/source.csv)",
    )
    # KW: 没必要传入output，直接把结果保存在/opt/ml/processing/output目录下
    # parser.add_argument(
    #     "--output_result",
    #     type=str,
    #     required=True,
    #     help="Output csv file path & name (e.g., ml/processing/output)",
    # )
    # KW: 也可以约定好/opt/ml/processing/code目录，而不用每次传入
    parser.add_argument(
        "--source_dir",
        type=str,
        required=True,
        help="The directory that has the Python source code and the requirements.txt (e.g., /opt/ml/processing/code)",
    )

    args = parser.parse_args()

    prepare_env(args.source_dir)
    mk_content = pass_data(args.input_csv)
    if mk_content:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        rand_digits = f"{random.randint(0, 9999):04d}"
        saved_file_name = (
            f"/opt/ml/processing/output/result_{timestamp}_{rand_digits}.md"
        )
        print(f">>>> Saving markdown content to {saved_file_name}")
        save_data(mk_content, saved_file_name)
