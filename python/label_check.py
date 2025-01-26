import os
import numpy as np
import cv2
import argparse

def load_labels(labels_file):
    """
    npyファイルからラベルデータを読み込む

    Args:
        labels_file (str): ラベルの .npy ファイルのパス

    Returns:
        np.ndarray: ラベル情報
    """
    if not os.path.exists(labels_file):
        print(f"Error: Labels file {labels_file} not found!")
        return None

    return np.load(labels_file)

def visualize_labeled_images(images_dir, labels_file, class_names):
    """
    画像とラベルデータを可視化しながらデバッグするツール

    Args:
        images_dir (str): 画像ディレクトリのパス
        labels_file (str): ラベルデータ (.npy) のパス
        class_names (dict): クラスIDと名前のマッピング
    """
    # 画像リストを取得
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    if not image_files:
        print("Error: No images found in the directory!")
        return

    # ラベルデータをロード
    labels_data = load_labels(labels_file)
    if labels_data is None:
        return

    total_images = len(image_files)
    index = 0  # 最初の画像から開始

    while True:
        image_path = os.path.join(images_dir, image_files[index])
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not load image {image_files[index]}")
            continue

        # 該当画像のラベルを取得
        image_timestamp = int(image_files[index].split('.')[0])  # ファイル名がタイムスタンプと仮定
        labels = labels_data[labels_data['t'] == image_timestamp]

        # バウンディングボックスの描画
        for label in labels:
            x, y, w, h, class_id, conf, track_id = label['x'], label['y'], label['w'], label['h'], label['class_id'], label['class_confidence'], label['track_id']
            class_name = class_names.get(class_id, "Unknown")

            # 緑色のバウンディングボックスを描画
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label_text = f"{class_name} ID:{track_id} ({conf:.2f})"
            cv2.putText(frame, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 画像を表示
        cv2.imshow("Labeled Image Debugger", frame)

        # ユーザー操作の受付
        key = cv2.waitKey(0) & 0xFF

        if key == ord('q'):  # 'q' で終了
            break
        elif key == ord('n'):  # 'n' で次の画像
            index = (index + 1) % total_images
        elif key == ord('p'):  # 'p' で前の画像
            index = (index - 1) % total_images

    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ラベル付されたデータをデバッグ＆可視化するツール")
    parser.add_argument("-i", "--images_dir", required=True, help="画像ディレクトリへのパス")
    parser.add_argument("-l", "--labels_file", required=True, help="ラベルデータ (.npy) ファイルのパス")

    args = parser.parse_args()

    # クラスIDと名前の対応表 (適宜変更)
    CLASS_NAMES = {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        4: "bus",
    }

    visualize_labeled_images(args.images_dir, args.labels_file, CLASS_NAMES)
