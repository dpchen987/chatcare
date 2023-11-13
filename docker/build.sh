#!/bin/bash

version=$(python get_version.py)
echo "version: $version"

# build .whl
sh build_whl.sh

# build hnswlib wheel for docker
hnswlib_whl=hnswlib-0.7.0-cp38-cp38-linux_x86_64.whl
if [ -f "$hnswlib_whl" ]; then
  echo "has $hnswlib_whl"
else
  pip wheel hnswlib==0.7.0
fi

# generate local workspace
cp ../requirements.txt .
# mkdir -p ./workspace/models/
cp -rLp /workspace/knowledge_base ./workspace/
cp -rLp /workspace/models/bge-base-zh ./workspace/models/
cp -rp /workspace/models/embedding_classify.pt ./workspace/models
cp -rp /workspace/models/intention_classify.pt ./workspace/models
chmod -R 777 workspace
# generate Docerfile
# cat << EOF > Dockerfile
# FROM python:3.8-slim
# WORKDIR /app
# ENV TZ="Asia/Shanghai"
# COPY requirements.txt $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl /app/
# RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt \
#     && pip install --no-cache-dir $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl \
#     && rm $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl

# CMD [ "chatcare"]
# EOF
cat << EOF > Dockerfile
FROM python:3.8-slim
WORKDIR /app
ENV TZ="Asia/Shanghai"
COPY requirements.txt /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt
COPY $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl /app/
RUN pip install --no-cache-dir $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl \
 && rm $hnswlib_whl chatcare-$version-cp38-cp38-linux_x86_64.whl

CMD [ "chatcare"]
EOF

# build docker
docker build -t chatcare:$version .
# if meet the Error:
#     W: GPG error: http://mirrors.tuna.tsinghua.edu.cn/debian buster InRelease: At least one invalid signature was encountered.
#     E: The repository 'http://mirrors.tuna.tsinghua.edu.cn/debian buster InRelease' is not signed.
# try to fix it with the command:
#     docker container prune

# save docker image, give it to IT guys for deploying
docker save -o image-chatcare-$version-`date "+%Y-%m-%d_%H.%M.%S"`.tar chatcare:$version

# clear
rm chatcare-$version-cp*-cp*-linux_x86_64.whl
rm requirements.txt
# rm -rf workspace
