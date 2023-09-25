FROM python:3.8-slim
WORKDIR /app
ENV TZ="Asia/Shanghai"
COPY requirements.txt hnswlib-0.7.0-cp38-cp38-linux_x86_64.whl chatcare-1.1.1-cp38-cp38-linux_x86_64.whl /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt     && pip install --no-cache-dir hnswlib-0.7.0-cp38-cp38-linux_x86_64.whl chatcare-1.1.1-cp38-cp38-linux_x86_64.whl     && rm hnswlib-0.7.0-cp38-cp38-linux_x86_64.whl chatcare-1.1.1-cp38-cp38-linux_x86_64.whl

CMD [ "chatcare"]
