import os
import subprocess
import argparse
from pathlib import Path

def get_subdirectories(directory):
    """ 指定ディレクトリ内のサブディレクトリのリストを取得 """
    return [str(d) for d in Path(directory).iterdir() if d.is_dir()]

def main(subdirs):

    for subdir in subdirs:
        cmd = ["python3", "python/track.py", "-b", subdir]
        subprocess.run(cmd)

        homography_path = os.path.join(subdir, "..", "homography_matrix.yaml")
        cmd = ["python3", "python/convert_labels.py", "-b", subdir, "-m",  homography_path]
        subprocess.run(cmd)
    

if __name__ == "__main__":

    # 引数のパース
    parser = argparse.ArgumentParser(description="Execute match_dataset.py on subdirectories")
    parser.add_argument("-i", "--input_dir", required=True, help="Base directory containing subdirectories")
    
    args = parser.parse_args()

    # サブディレクトリの取得
    subdirs = get_subdirectories(args.input_dir)

    # スクリプトを実行
    main(subdirs)