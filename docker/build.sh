#!/bin/bash

version=$(python get_version.py)
echo "version: $version"

# build .whl
sh build_whl.sh

# copy all needs to current dir
cp ../requirements.txt .
mkdir -p ./workspace/models/
cp -rL /workspace/knowledge_base ./workspace/
cp -rL /workspace/models/bge-base-zh ./workspace/models/
cp -r /workspace/models/embedding_classify.pt ./workspace/models
# build docker
docker build --build-arg version=$version -t chatcare:$version .
# if meet the Error:
#     W: GPG error: http://mirrors.tuna.tsinghua.edu.cn/debian buster InRelease: At least one invalid signature was encountered.
#     E: The repository 'http://mirrors.tuna.tsinghua.edu.cn/debian buster InRelease' is not signed.
# try to fix it with the command:
#     docker container prune

# save docker image, give it to IT guys for deploying
docker save -o image-chatcare-$version-`date "+%Y-%m-%d_%H:%M:%S"`.tar chatcare:$version

# clear
rm chatcare-$version-cp*-cp*-linux_x86_64.whl
rm requirements.txt
rm -rf workspace