#!/bin/bash

# 環境変数の設定
DATA_DIR="/home/apollo/Arata/gifu"  # データセットのディレクトリ
DEST_DIR="/home/apollo/dataset/gifu_pre"  # 前処理後のデータ保存先
NUM_PROCESSES=４  # 並列処理数

# const_durationの設定値リスト
DURATION_VALUES=(5 10 50 100)

# デバッグ用ログ出力
echo "DATA_DIR=${DATA_DIR}, DEST_DIR=${DEST_DIR}, NUM_PROCESSES=${NUM_PROCESSES}"

# エラーチェック
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: DATA_DIR does not exist -> $DATA_DIR"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
    echo "Warning: DEST_DIR does not exist -> Creating $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

# 時間計測開始
TOTAL_START_TIME=$(date +%s)

# ループで複数の const_duration 設定を適用
for DURATION in "${DURATION_VALUES[@]}"; do
    CONFIG_FILE="conf_preprocess/extraction/const_duration_${DURATION}.yaml"
    
    echo "Processing with ${CONFIG_FILE}..."
    
    START_TIME=$(date +%s)

    # 実行コマンド
    COMMAND=(
        python python/preprocess_rvt.py "$DATA_DIR" "$DEST_DIR"
        "conf_preprocess/representation/event_frame.yaml"
        "$CONFIG_FILE"
        "conf_preprocess/filter_gifu.yaml"
        -ds "gifu" -np "$NUM_PROCESSES"
    )

    # 実行
    if "${COMMAND[@]}"; then
        echo "Preprocessing completed successfully for duration=${DURATION}!"
    else
        echo "Error: Preprocessing failed for duration=${DURATION}!"
        exit 1
    fi

    END_TIME=$(date +%s)
    ELAPSED_TIME=$((END_TIME - START_TIME))

    echo "Execution Time for duration=${DURATION}: ${ELAPSED_TIME} seconds"
done

# 全体の時間計測終了
TOTAL_END_TIME=$(date +%s)
TOTAL_ELAPSED_TIME=$((TOTAL_END_TIME - TOTAL_START_TIME))

echo "Total Execution Time: ${TOTAL_ELAPSED_TIME} seconds"
