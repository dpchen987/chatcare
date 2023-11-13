# if it runs behind nginx path, add: -e ROOT_PATH=chatcare
docker run -d --restart=always -p 8001:8000 -e ROOT_PATH=chatcare -e ROOT_PATH=chatcare -v /workspace:/workspace --name chatcare chatcare:1.2.0
docker run -d --restart=always -p 8001:8000 -e ROOT_PATH=chatcare -e DB_PORT=3306 -v /workspace:/workspace --name chatcare chatcare:1.2.0
docker run -d --restart=always -p 8001:8000 -e ROOT_PATH=chatcare -e DB_PORT=3306 -v /home/dapeng/chatcare-1/docker/workspace:/workspace --name chatcare chatcare:1.2.0
# 本机测试
docker run -d --restart=always -p 8001:8000 -e ROOT_PATH=chatcare -e DB_HOST='47.101.138.4' -e DB_PORT=3308 -e DB_USER=ai_care -e DB_PASS=YIjia@1110 -v /home/dapeng/chatcare-1/docker/workspace:/workspace --name chatcare chatcare:1.2.0
# 生产部署
docker run -d --restart=always -p 8000:8000 -e DB_HOST='47.101.138.4' -e DB_PORT=3308 -e DB_USER=ai_care -e DB_PASS=YIjia@1110 -v /chat-ai/workspace:/workspace --name chatcare chatcare:1.2.0