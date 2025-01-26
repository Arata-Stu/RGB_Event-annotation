import os
import numpy as np
import cv2
import yaml
import argparse
from ultralytics import YOLO
from tqdm import tqdm

def load_exclusion_regions(base_dir):
    exclusion_regions = []
    txt_path = os.path.join(base_dir, ".." ,"exclusion_regions.txt")
    yaml_path = os.path.join(base_dir, "..", "exclusion_regions.yaml")

    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            for line in f:
                values = line.strip().split(",")
                if len(values) == 4:
                    exclusion_regions.append(tuple(map(int, values)))

    elif os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            if "exclusion_regions" in data:
                exclusion_regions.extend([tuple(region) for region in data["exclusion_regions"]])

    return exclusion_regions

def is_in_exclude_region(x1, y1, x2, y2, exclusion_regions, threshold=30):
    bbox_area = (x2 - x1) * (y2 - y1)
    if bbox_area <= 0:
        return False

    for x_min, y_min, x_max, y_max in exclusion_regions:
        inter_x1 = max(x1, x_min)
        inter_y1 = max(y1, y_min)
        inter_x2 = min(x2, x_max)
        inter_y2 = min(y2, y_max)
        
        inter_width = max(0, inter_x2 - inter_x1)
        inter_height = max(0, inter_y2 - inter_y1)
        inter_area = inter_width * inter_height
        
        overlap_ratio = (inter_area / bbox_area) * 100
        if overlap_ratio >= threshold:
            return True
    return False

def process_images(base_dir, target_classes, render_mode):
    images_dir = os.path.join(base_dir, "images")
    labels_dir = os.path.join(base_dir, "labels")
    os.makedirs(labels_dir, exist_ok=True)

    exclusion_regions = load_exclusion_regions(base_dir)
    print(f"Loaded exclusion regions: {exclusion_regions}")

    offset_file = os.path.join(base_dir, "image_offsets.txt")
    if not os.path.exists(offset_file):
        print("Error: image_offsets.txt not found.")
        return

    with open(offset_file, "r") as f:
        timestamps = [int(line.strip()) for line in f.readlines()]

    camera_dirs = [
        d for d in os.listdir(images_dir)
        if os.path.isdir(os.path.join(images_dir, d)) and "camera" in d
    ]

    if not camera_dirs:
        print("Error: No camera directories found in the images directory.")
        return

    model = YOLO("yolo11x.pt")

    for camera_dir in camera_dirs:
        camera_path = os.path.join(images_dir, camera_dir)
        output_file = os.path.join(labels_dir, f"{camera_dir}_labels_events.npy")

        image_files = sorted([
            f for f in os.listdir(camera_path)
            if f.endswith(('.png', '.jpg', '.jpeg'))
        ])

        if not image_files:
            print(f"Warning: No image files found in the directory {camera_dir}.")
            continue

        print(f"Processing directory: {camera_dir}")

        all_data = []

        for idx, image_file in enumerate(tqdm(image_files, desc=f"Processing {camera_dir}")):
            image_path = os.path.join(camera_path, image_file)
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"Failed to load image: {image_file}")
                continue

            results = model.track(
                source=frame,
                persist=True,
                tracker="bytetrack.yaml"
            )

            timestamp = timestamps[idx] if idx < len(timestamps) else -1

            if render_mode:
                for x_min, y_min, x_max, y_max in exclusion_regions:
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

            if results is not None:
                for result in results:
                    boxes = result.boxes.xyxy
                    confs = result.boxes.conf
                    cls_ids = result.boxes.cls.int().cpu().tolist()
                    track_ids = result.boxes.id.cpu().tolist() if result.boxes.id is not None else [-1] * len(cls_ids)

                    for box, class_confidence, cls_id, track_id in zip(boxes, confs, cls_ids, track_ids):
                        x1, y1, x2, y2 = map(int, box)
                        class_name = model.names[cls_id]

                        if is_in_exclude_region(x1, y1, x2, y2, exclusion_regions, threshold=30):
                            continue

                        if not target_classes or class_name in target_classes:
                            all_data.append((
                                timestamp,
                                x1, y1, x2 - x1, y2 - y1,
                                cls_id, float(class_confidence), track_id
                            ))

                            if render_mode:
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                label_text = f"{class_name} {track_id}"
                                cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if render_mode:
                cv2.imshow("YOLO Detection with Exclusion Zones", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Process interrupted by user.")
                    cv2.destroyAllWindows()
                    return

        np.save(output_file, np.array(all_data))
        print(f"Saved: {output_file}")

    if render_mode:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLOで画像を解析し、リアルタイムGUI表示するスクリプト")
    parser.add_argument("-b", "--base_dir", required=True, help="ベースディレクトリへのパス")
    parser.add_argument("-c", "--classes", nargs='*', default=["car", "bicycle", "person", "motorcycle", "bus"], help="検出対象クラス")
    parser.add_argument("--render", action='store_true', help="GUI表示を有効化する")
    
    args = parser.parse_args()
    process_images(args.base_dir, args.classes, args.render)
