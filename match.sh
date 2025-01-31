## input output directory を取得
input_dir=$1
output_dir=$2

# データセットのマッチング
python3 python/match_dataset.py -i ${input_dir} -o ${output_dir}

## 完了を通知
echo "Matching completed successfully!"