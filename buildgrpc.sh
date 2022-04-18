echo "PROTOBUF: $PROTOBUF"

if [ ! -d "./include/" ];then
    mkdir ./include
fi

GOOGLE_API="./include/googleapis"

echo "准备依赖文件......"

if [ ! -d $GOOGLE_API ];then
    pushd ./include
    git clone https://github.com/googleapis/googleapis.git
    popd -1
fi

echo "编译Python的GRPC......"

python3 -m grpc_tools.protoc -I=./nutbox_bot/grpc \
    -I=$GOOGLE_API \
    --python_out=./nutbox_bot/grpc \
    --grpc_python_out=./nutbox_bot/grpc \
    ./nutbox_bot/grpc/nutbox_bot.proto