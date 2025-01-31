## input output directory を取得
input_dir=$1


## 引数確認 
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_dir>"
    exit 1
fi

## サブディレクトリを取得
sub_dirs=$(find ${input_dir} -mindepth 1 -maxdepth 1 -type d)

## loop
for sub_dir in ${sub_dirs}; do
    
    ## h5を作成 
    python3 python/track.py -b ${sub_dir} --render

    python3 python/convert_labels.py -b ${sub_dir}

## 完了を通知
echo "Matching completed successfully!"
done