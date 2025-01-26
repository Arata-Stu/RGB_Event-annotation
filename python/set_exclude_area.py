import cv2
import yaml
import os

# 除外領域リスト
exclusion_regions = []
drawing = False
start_x, start_y = -1, -1

def draw_rectangle(event, x, y, flags, param):
    global start_x, start_y, drawing, exclusion_regions

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_img = img.copy()
            cv2.rectangle(temp_img, (start_x, start_y), (x, y), (0, 255, 0), 2)
            cv2.imshow("Select Exclusion Areas", temp_img)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_x, end_y = x, y
        # x_min, y_min, x_max, y_max の順で保存
        exclusion_regions.append((min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y)))
        cv2.rectangle(img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        cv2.imshow("Select Exclusion Areas", img)

def save_exclusion_regions(base_dir, save_format="txt"):
    """ 除外領域を指定フォーマットで保存 """
    txt_path = os.path.join(base_dir, "exclusion_regions.txt")
    yaml_path = os.path.join(base_dir, "exclusion_regions.yaml")

    if save_format == "txt":
        with open(txt_path, "w") as f:
            for region in exclusion_regions:
                f.write(",".join(map(str, region)) + "\n")
        print(f"Saved exclusion regions to {txt_path}")

    elif save_format == "yaml":
        data = {"exclusion_regions": exclusion_regions}
        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
        print(f"Saved exclusion regions to {yaml_path}")

if __name__ == "__main__":
    base_dir = input("Enter the base directory: ").strip()
    image_path = input("Enter the path to an example image: ").strip()

    if not os.path.exists(image_path):
        print("Error: Image file not found.")
        exit()

    img = cv2.imread(image_path)
    cv2.imshow("Select Exclusion Areas", img)
    cv2.setMouseCallback("Select Exclusion Areas", draw_rectangle)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESCキーで終了
            break
        elif key == ord("s"):  # 's'キーで保存
            save_format = input("Save as 'txt' or 'yaml'?: ").strip().lower()
            save_exclusion_regions(base_dir, save_format)
        elif key == ord("r"):  # 'r'キーでリセット
            exclusion_regions.clear()
            img = cv2.imread(image_path)
            cv2.imshow("Select Exclusion Areas", img)

    cv2.destroyAllWindows()
