# chatcare-api-server


## 参数

- `PORT <int>`: 默认为`8000`，api port；
- `HOST <str>`: 默认为`0.0.0.0`，api host；
- `CHAT_MODE <str>`: 默认为`llm`，主接口v1/chat/completions对话模式，`llms`：大模型 or `se`：搜索引擎 or `kb`：llm+知识库(待开发)；
- `DEBUG <bool>`: 默认为`True`，debug模式，用于冗余信息输出；