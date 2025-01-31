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

    output_file = os.path.join(event_dir,"events.h5")

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
