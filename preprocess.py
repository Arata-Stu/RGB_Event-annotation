import os
import subprocess
import time


def main():
    # 環境変数の設定
    DATA_DIR = "/home/arata22/dataset/gifu"  # データセットのディレクトリ
    DEST_DIR = "/home/arata22/dataset/gifu_pre"  # 前処理後のデータ保存先
    NUM_PROCESSES = 1  # 並列処理数

    # デバッグ用ログ出力
    print(f"DATA_DIR={DATA_DIR}, DEST_DIR={DEST_DIR}, NUM_PROCESSES={NUM_PROCESSES}")

    # エラーチェック
    if not os.path.isdir(DATA_DIR):
        print(f"Error: DATA_DIR does not exist -> {DATA_DIR}")
        exit(1)

    if not os.path.isdir(DEST_DIR):
        print(f"Warning: DEST_DIR does not exist -> Creating {DEST_DIR}")
        os.makedirs(DEST_DIR, exist_ok=True)

    # 実行コマンド
    command = [
        "python", "python/preprocess_rvt.py", DATA_DIR, DEST_DIR,
        "conf_preprocess/representation/event_frame.yaml",
        "conf_preprocess/extraction/const_duration_20.yaml",
        "conf_preprocess/filter_gifu.yaml",
        "-ds", "gifu", "-np", str(NUM_PROCESSES)
    ]

    # 時間計測開始
    start_time = time.time()

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Preprocessing completed successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error: Preprocessing failed!")
        print(e.stderr)
        exit(1)

    # 時間計測終了
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution Time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
