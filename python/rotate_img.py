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

def process_sequence_dir(sequence_path):
    """ sequenceディレクトリ内の全カメラディレクトリを処理 """
    images_path = os.path.join(sequence_path, "images")
    if not os.path.isdir(images_path):
        print(f"Error: imagesディレクトリが存在しません -> {images_path}")
        sys.exit(1)

    print(f"Processing sequence: {sequence_path}")
    for folder in os.scandir(images_path):
        if "camera" in folder.name and folder.is_dir():
            print(f"Processing: {folder.path}")
            process_directory(folder.path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate all images in the specified sequence directory.")
    parser.add_argument("--base_dir", "-b", required=True, help="Sequence directory containing images directory")
    args = parser.parse_args()

    process_sequence_dir(args.base_dir)
