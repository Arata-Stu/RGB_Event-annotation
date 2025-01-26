import os
import subprocess
import argparse
from pathlib import Path

def get_subdirectories(directory):
    """ 指定ディレクトリ内のサブディレクトリのリストを取得 """
    return [str(d) for d in Path(directory).iterdir() if d.is_dir()]

def execute_script(subdirs, output_base_dir, rotate):
    """ 各サブディレクトリごとに出力ディレクトリを作成し、処理を実行 """
    for subdir in subdirs:
        subdir_name = os.path.basename(subdir)
        output_dir = os.path.join(output_base_dir, subdir_name)  # 各サブディレクトリの出力フォルダ
        os.makedirs(output_dir, exist_ok=True)  # 出力ディレクトリ作成

        # match_dataset.py 実行
        cmd = ["python3", "python/match_dataset.py", "-i", subdir, "-o", output_dir]
        print(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd)

        ## raw -> hdf5
        cmd = ["metavision_file_to_hdf5", "-i", output_base_dir, "-r", "-p", ".*\\.raw"]
        print(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd)

        # hdf5 -> rotated format h5
        subdirs = get_subdirectories(output_dir)
        print(f"Subdirectories: {subdirs}")
        for subdir in subdirs:
            cmd = ["python3", "python/convert_h5.py", "-b", subdir, "-W", "640", "-H", "480"]
            if rotate:
                cmd.append("-r")  # rotate オプション追加
                cmd.append("True")

            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd)

        # RGB rotate (オプション)
        if rotate:
            cmd = ["python3", "python/rotate_img.py", "-b", output_dir]
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd)

if __name__ == "__main__":
    # 引数のパース
    parser = argparse.ArgumentParser(description="Execute match_dataset.py on subdirectories")
    parser.add_argument("-i", "--input_dir", required=True, help="Base directory containing subdirectories")
    parser.add_argument("-o", "--output_dir", required=True, help="Output directory for results")
    parser.add_argument("-r", "--rotate", action="store_true", help="Apply 180-degree rotation")

    args = parser.parse_args()

    # サブディレクトリの取得
    subdirs = get_subdirectories(args.input_dir)

    # スクリプトを実行
    execute_script(subdirs, args.output_dir, args.rotate)
