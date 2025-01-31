## input output directory を取得
input_dir=$1
## rotateをTrueにするかどうか boolで取得
rotate=$2

## 引数確認 
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_dir> <rotate>"
    exit 1
fi
## hdf5を作成
# metavision_file_to_hdf5 -i ${input_dir} -r -p ".*\\.raw"

## input_dir内のサブディレクトリを取得
sub_dirs=$(find ${input_dir} -mindepth 1 -maxdepth 1 -type d)

## loop
for sub_dir in ${sub_dirs}; do
    
    ## h5を作成 
    python3 python/convert_h5.py -b ${sub_dir} -W 640 -H 480 -r ${rotate}

    ## 画像のrotate
    # if [ ${rotate} = "True" ]; then
    #     python3 python/rotate_img.py -b ${sub_dir}
    # fi


done


## 完了を通知
echo "Matching completed successfully!"