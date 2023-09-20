# if it runs behind nginx path, add: -e ROOT_PATH=chatcare
docker run -d --restart=always -p 8009:8009 -e PORT=8009  --name chatcare chatcare:1.1.0
