# docker build
./ build.sh

# docker run
docker run -d --restart=always -p 8001:8000 -v $(pwd)/workspace:/workspace chatcare:1.1.1

# 注：宿主机中不能有软连接，不然报错

# 拷贝到阿里云服务器
scp -r -P 2222 ./workspace/* dapeng@139.196.174.7:/workspace/ 
scp -r -P 2222 ./image-chatcare-1.1.1-2023-09-21_13.31.38.tar dapeng@139.196.174.7:/mnt/ai/share/chatcare_pkgs