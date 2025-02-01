## input 
input_dir=$1

## rotate bool
rotate=$2

## 引数確認
if [ $# -ne 2 ]; then
    echo "Usage: $0 input_dir rotate"
    exit 1
fi


## input_dirのサブディレクトリを取得
sub_dirs=`ls -d ${input_dir}/*`

## loop
for sub_dir in ${sub_dirs}
do
    ## ディレクトリ名を取得
    dir_name=`basename ${sub_dir}`
    echo ${dir_name}

    bash create_h5.sh ${sub_dir} ${rotate}

    bash annotate.sh ${sub_dir}


    ## ディレクトリ内のファイルを取得
    files=`ls ${sub_dir}/*`

    
done