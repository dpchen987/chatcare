FROM python:3.8-slim
ARG version
WORKDIR /app
ENV TZ="Asia/Shanghai"
# 
COPY requirements.txt /app
# RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free"  > /etc/apt/sources.list \
    && apt-get update && apt-get install -y g++ libgomp1 \
    && pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt \
    && apt-get remove -y g++ && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/*
    
COPY chatcare-0.1-cp38-cp38-linux_x86_64.whl /app
RUN pip install --no-cache-dir chatcare-0.1-cp38-cp38-linux_x86_64.whl && rm chatcare-0.1-cp38-cp38-linux_x86_64.whl

COPY workspace /workspace

CMD [ "chatcare"]