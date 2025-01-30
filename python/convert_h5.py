# import h5py
# import glob
# import argparse
# import os
# import numpy as np

# def convert_hdf5(base_dir, W, H, rotate):
#     event_dir = os.path.join(base_dir, "events")

#     # eventsディレクトリ内の.hdf5ファイルを探索
#     hdf5_files = glob.glob(os.path.join(event_dir, "*.hdf5"))
#     if len(hdf5_files) == 1:
#         input_file = hdf5_files[0]
#         print("Found HDF5 file:", input_file)
#     elif len(hdf5_files) > 1:
#         print("Warning: Multiple HDF5 files found:", hdf5_files)
#         return
#     else:
#         print("No HDF5 file found in", event_dir)
#         return

#     output_file = "events.h5"

#     # HDF5ファイルを開く
#     with h5py.File(input_file, "r") as f_in, h5py.File(output_file, "w") as f_out:
#         if "/CD/events" in f_in:
#             dset_in = f_in["/CD/events"]

#             # データセットの shape, dtype を取得
#             shape = dset_in.shape
#             dtype = dset_in.dtype

#             # データセットのカラム名を取得
#             column_names = dset_in.dtype.names
#             print("データのカラム名:", column_names)

#             # (x, y) 座標のカラムを特定
#             x_col = "x" if "x" in column_names else None
#             y_col = "y" if "y" in column_names else None

#             if x_col is None or y_col is None:
#                 print("エラー: 'x' または 'y' カラムが見つかりません。")
#                 return

#             print(f"画像サイズ: width={W}, height={H}")

#             # データを numpy 配列として読み込む
#             data = dset_in[:]

#             # 180度回転が有効なら (x, y) を変換
#             if rotate:
#                 data[x_col] = W - 1 - data[x_col]
#                 data[y_col] = H - 1 - data[y_col]
#                 print("180度回転を適用しました。")
#             else:
#                 print("回転なしでコピーします。")

#             # 新しいデータセットを /events に作成（圧縮なし）
#             dset_out = f_out.create_dataset("/events", shape, dtype=dtype, data=data)

#             # 既存の属性をコピー
#             for attr_name, attr_value in dset_in.attrs.items():
#                 dset_out.attrs[attr_name] = attr_value

#             print(f"/CD/events を {'180度回転して ' if rotate else ''}/events に保存しました。")
#         else:
#             print("データセット /CD/events が見つかりません。")

#     print(f"新しいファイルを {output_file} に保存しました。")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Convert .hdf5 file to .h5 with optional dataset renaming and 180-degree rotation.")
#     parser.add_argument("--base_dir", "-b", help="Path to the input directory includes .hdf5 file")
#     parser.add_argument("--width", "-W", default=640, type=int, help="Width of the image")
#     parser.add_argument("--height", "-H", default=480, type=int, help="Height of the image")
#     parser.add_argument("--rotate", "-r", default=False, type=bool, help="Apply 180-degree rotation")
#     args = parser.parse_args()

#     if not os.path.exists(args.base_dir):
#         print(f"入力ファイル {args.base_dir} が見つかりません。")
#     else:
#         convert_hdf5(args.base_dir, args.width, args.height, args.rotate)

import h5py
import glob
import argparse
import os
import numpy as np

def convert_hdf5(base_dir, W, H, rotate):
    event_dir = os.path.join(base_dir, "events")

    # eventsディレクトリ内の.hdf5ファイルを探索
    hdf5_files = glob.glob(os.path.join(event_dir, "*.hdf5"))
    if len(hdf5_files) == 1:
        input_file = hdf5_files[0]
        print("Found HDF5 file:", input_file)
    elif len(hdf5_files) > 1:
        print("Warning: Multiple HDF5 files found:", hdf5_files)
        return
    else:
        print("No HDF5 file found in", event_dir)
        return

    output_file = "events.h5"

    # HDF5ファイルを開く
    with h5py.File(input_file, "r") as f_in, h5py.File(output_file, "w") as f_out:
        if "/CD/events" in f_in:
            dset_in = f_in["/CD/events"]
            data = dset_in[:]

            # MetavisionのデータをDSECフォーマットに変換
            x_data = data["x"].astype(np.uint16)
            y_data = data["y"].astype(np.uint16)
            t_data = data["t"].astype(np.uint64)
            p_data = data["p"].astype(np.uint8)

            if rotate:
                x_data = W - 1 - x_data
                y_data = H - 1 - y_data
                print("180度回転を適用しました。")
            else:
                print("回転なしでコピーします。")

            # DSEC形式に保存
            grp = f_out.create_group("events")
            grp.create_dataset("x", data=x_data, dtype="u2")
            grp.create_dataset("y", data=y_data, dtype="u2")
            grp.create_dataset("t", data=t_data, dtype="u8")
            grp.create_dataset("p", data=p_data, dtype="u1")

            
            print("変換が完了しました。")
        else:
            print("データセット /CD/events が見つかりません。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Metavision .hdf5 to DSEC-compatible .h5")
    parser.add_argument("--base_dir", "-b", required=True, help="Path to the input directory")
    parser.add_argument("--width", "-W", default=640, type=int, help="Image width")
    parser.add_argument("--height", "-H", default=480, type=int, help="Image height")
    parser.add_argument("--rotate", "-r", action="store_true", help="Apply 180-degree rotation")
    args = parser.parse_args()

    convert_hdf5(args.base_dir, args.width, args.height, args.rotate)
