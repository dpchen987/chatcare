#!/bin/bash

version=$(python get_version.py)
echo "version: $version"
pyversion=310

# build .whl
sh build_whl.sh

chatcare_whl=chatcare2-$version-cp$pyversion-cp$pyversion-linux_x86_64.whl

cp ../chatcare2/requirements.txt .

# gen Dockerfile
cat << EOF > Dockerfile
FROM python:3.10-slim
WORKDIR /app
ENV TZ="Asia/Shanghai"
COPY requirements.txt /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt
COPY $chatcare_whl /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir $chatcare_whl && rm $chatcare_whl

CMD [ "chatcare"]
EOF

# build docker
docker build -t chatcare:$version .

# save docker image, give it to IT guys for deploying
# docker save -o image-chatcare-$version-`date "+%Y-%m-%d_%H.%M.%S"`.tar chatcare:$version

# clear
# rm chatcare-$version-cp*-cp*-linux_x86_64.whl
rm requirements.txt
# rm -rf workspace
