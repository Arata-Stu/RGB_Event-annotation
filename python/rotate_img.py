import os
import sys
import concurrent.futures
from PIL import Image
import argparse

def rotate_image(img_path):
    """ 画像を180度回転させて上書き保存 """
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGB")  # 高速化のため明示的にRGB変換
            img = img.rotate(180)
            img.save(img_path, "JPEG")
        print(f"Processed: {img_path}")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

def process_directory(camera_path):
    """ 指定されたカメラディレクトリ内の全画像を並列処理 """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for entry in os.scandir(camera_path):
            if entry.is_file() and entry.name.lower().endswith(".jpg"):
                futures.append(executor.submit(rotate_image, entry.path))
        
        # すべてのスレッドの完了を待機
        concurrent.futures.wait(futures)

def process_base_dir(base_dir):
    """ base_dir内の全カメラディレクトリを処理 """
    if not os.path.isdir(base_dir):
        print(f"Error: 指定したディレクトリが存在しません -> {base_dir}")
        sys.exit(1)

    print(f"Processing base directory: {base_dir}")
    for sequence in os.scandir(base_dir):
        sequence_path = os.path.join(sequence.path, "images")
        print(f"Processing sequence: {sequence_path}")
        if not os.path.isdir(sequence_path):
            print(f"Error: imagesディレクトリが存在しません -> {sequence_path}")
            continue
        
        for folder in os.scandir(sequence_path):
            if "camera" in folder.name and folder.is_dir():
                print(f"Processing: {folder.path}")
                process_directory(folder.path)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Rotate all images in the specified directory.")
    parser.add_argument("--base_dir", "-b", required=True, help="Base directory containing camera directories")
    args = parser.parse_args()

    process_base_dir(args.base_dir)