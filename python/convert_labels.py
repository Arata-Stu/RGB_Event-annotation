import os
import numpy as np
import argparse
import yaml
from tqdm import tqdm

def load_homography(matrix_path, camera_name):
    """YAMLファイルからホモグラフィ行列を読み込む"""
    with open(matrix_path, 'r') as f:
        data = yaml.safe_load(f)
    
    if camera_name not in data['homography_matrix']:
        raise ValueError(f"Camera {camera_name} not found in the homography matrix file.")

    return np.array(data['homography_matrix'][camera_name])

def apply_homography(H, points):
    """ホモグラフィ行列を適用して点を変換"""
    num_points = points.shape[0]
    homogenous_points = np.hstack([points, np.ones((num_points, 1))])
    transformed_points = (H @ homogenous_points.T).T
    transformed_points /= transformed_points[:, 2][:, None]
    return transformed_points[:, :2]

def transform_bbox_with_homography(H, bbox):
    """バウンディングボックスをホモグラフィ変換"""
    x, y, w, h = bbox
    x_min = x
    y_min = y
    x_max = x + w
    y_max = y + h

    corners = np.array([
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ])
    transformed_corners = apply_homography(H, corners)
    x_min, y_min = np.min(transformed_corners, axis=0)
    x_max, y_max = np.max(transformed_corners, axis=0)

    new_x = x_min
    new_y = y_min
    new_w = x_max - x_min
    new_h = y_max - y_min

    return new_x, new_y, new_w, new_h

def process_labels(base_dir, matrix_path):
    """YOLOの推論結果をホモグラフィ変換し、全カメラ統合して `labels_events.npy` に保存"""
    labels_dir = os.path.join(base_dir, "labels")
    output_file = os.path.join(labels_dir, "labels_events.npy")
    
    if not os.path.exists(labels_dir):
        print("Error: labels directory not found.")
        return
    
    label_files = [
        f for f in os.listdir(labels_dir)
        if f.endswith('.npy') and "camera" in f
    ]
    
    if not label_files:
        print("Error: No label files found in the labels directory.")
        return
    
    all_transformed_data = []

    for label_file in label_files:
        camera_name = label_file.replace("_labels_events.npy", "")

        input_file = os.path.join(labels_dir, label_file)

        try:
            homography_matrix = load_homography(matrix_path, camera_name)
            print(f"Loaded homography matrix for {camera_name}:\n{homography_matrix}")  # デバッグ用
        except ValueError as e:
            print(e)
            continue
        
        print(f"Processing {label_file} with homography transformation.")

        # npyファイルのロード
        data = np.load(input_file)
        print(f"Loaded {label_file}: {data.shape}")  # デバッグ用

        if data.size == 0:
            print(f"Warning: {label_file} is empty. Skipping.")
            continue

        transformed_data = []
        
        for entry in tqdm(data, desc=f"Transforming {label_file}"):
            timestamp, x, y, w, h, class_id, conf, track_id = entry
            transformed_bbox = transform_bbox_with_homography(homography_matrix, (x, y, w, h))
            print(f"Original bbox: {(x, y, w, h)}, Transformed bbox: {transformed_bbox}")  # デバッグ用

            if np.isnan(transformed_bbox).any():
                print(f"Warning: Invalid transformed bbox for {label_file}, skipping entry.")
                continue

            transformed_data.append((
                int(timestamp),  # タイムスタンプ
                int(transformed_bbox[0]),  # x座標
                int(transformed_bbox[1]),  # y座標
                int(transformed_bbox[2]),  # 幅
                int(transformed_bbox[3]),  # 高さ
                int(class_id),  # クラスID
                float(conf),  # 信頼度
                int(track_id)  # トラッキングID
            ))
        
        all_transformed_data.extend(transformed_data)

    print(f"Total transformed entries: {len(all_transformed_data)}")  # デバッグ用

    if len(all_transformed_data) == 0:
        print("Error: No valid transformed data. Output will be empty.")
        return

    # NumPy structured array の dtype を定義
    dtype_labels = np.dtype([
        ('t', 'int64'),    # タイムスタンプ
        ('x', 'int32'),    # x座標 (左上)
        ('y', 'int32'),    # y座標 (左上)
        ('w', 'int32'),    # 幅
        ('h', 'int32'),    # 高さ
        ('class_id', 'int32'),  # クラスID
        ('class_confidence', 'float32'),    # 信頼度
        ('track_id', 'int32')   # トラッキングID
    ])
    
    # NumPy 配列に変換
    all_transformed_data_array = np.array(all_transformed_data, dtype=dtype_labels)
    
    # npy ファイルとして保存
    np.save(output_file, all_transformed_data_array)
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="YOLOの推論結果をホモグラフィ変換し、全カメラのデータを統合して `labels_events.npy` に保存します。"
    )
    parser.add_argument("-b", "--base_dir", required=True, help="ベースディレクトリへのパス")
    parser.add_argument("-m", "--matrix", required=True, help="ホモグラフィ行列（YAMLファイル）へのパス")

    args = parser.parse_args()
    process_labels(args.base_dir, args.matrix)
