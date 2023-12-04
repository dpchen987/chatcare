# Visit http://localhost:8000/docs (default) for documents.

import time
import uuid
import json
import torch
import uvicorn
from typing import Annotated

from fastapi import FastAPI, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse

from chatcare2.utils.types import (
    ChatKnowledgeBaseRequest,
    ChatKnowledgeBaseResponse
)
from chatcare2.utils.logger import logger
from chatcare2 import __version__
from chatcare2.config import params
from chatcare2.chains import chain_multi_turn


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def create_app():
    app = FastAPI(
        title="chatcare2 API Server",
        version=__version__,
        lifespan=lifespan,
    )
    # 跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Test page
    app.mount("/static", StaticFiles(directory="/workspace/knowledge_base/"), name="static")
    html_path = '/workspace/knowledge_base/html/chat.html'
    
    @app.get('/', response_class=HTMLResponse)
    async def home():
        if params.debug:
            with open(html_path) as f:
                html = f.read()
        else:
            html = '<b>not debug running</b>'
        return html

    # Tag: Chat
    @app.post(
        "/v1/chat/multi_turn",
        tags=["Chat"],
        summary="chatcare2对话主接口",
        response_model=ChatKnowledgeBaseResponse
    )
    async def chat_multi_turn(
        chat_request: ChatKnowledgeBaseRequest,
        response: Response,
        chat_id: Annotated[str | None, Cookie()] = None,
    ) -> ChatKnowledgeBaseResponse:
        """chatcare2对话接口: 旧版，标准http 协议，增加GPT
        """
        if not chat_id:
            chat_id = str(uuid.uuid4())
        logger.info(f"---chatid :{chat_id} ~---")
        response.set_cookie(key='chat_id', value=chat_id)
        query = chat_request.messages[-1].content
        answer = chain_multi_turn.chain(query, chat_id)
        answer['error'] = 0
        if answer['intent_id'] == '0':
            logger.info('=== Asking GPT ===')
            b = time.time()
            content = await chain_multi_turn.gpt(chat_id, query)
            e = round(time.time() - b, 2)
            answer['summary'] = content
            logger.info(f'=== Asking GPT time used: {e} seconds. ===')
        res = ChatKnowledgeBaseResponse(**answer)
        return res

    # Tag: ChatSSE
    @app.post(
        "/v1/chat/multi_turn_sse",
        tags=["ChatSSE"],
        summary="chatcare2对话主接口, SSE",
        response_model=ChatKnowledgeBaseResponse
    )
    async def chat_multi_turn_sse(
        chat_request: ChatKnowledgeBaseRequest
    ) -> ChatKnowledgeBaseResponse:
        """chatcare2对话接口
        调用此接口的过程：
        1. 通过POST发送数据；POST时开启stream（流式），以便通过SSE接收数据。

        Python requests 示例：
        ```python
        stream = requests.post('api-url", stream=True, json=data)
        ```
        非 Python requests 库可参考逻辑：流式本质上是先post数据建立连接，不立即下载全部响应数据，而是通过SSE方式边下载边解析。

        2. 通过SSE方式接受数据；

        输入参数：

            chat_id: 会话ID以区分不同用户的聊天，可以是用户ID.

            message: 聊天消息，格式详见下面示例。

        输出：

            Server-Sent Events, 通过'event'标签区分是知识库回答，还是GPT回答：

            event 值是'knowledge_base'时为知识库回答，其它为GPT回答。
        """
        chat_id = chat_request.chat_id
        logger.info(f"---chatid :{chat_id} ~---")
        query = chat_request.messages[-1].content
        answer = chain_multi_turn.chain(query, chat_id)
        if answer['intent_id'] == '0':
            logger.info('=== Asking GPT ===')
            generator = chain_multi_turn.gpt(query)
            logger.info('=== Asking GPT generator ===')
            return EventSourceResponse(generator)

        async def kb_generator():
            yield {
                'event': 'knowledge_base',
                'id': 0,
                'data': json.dumps(answer, ensure_ascii=False)
            }
        return EventSourceResponse(kb_generator())

    return app


app = create_app()


def run_api():
    uvicorn.run(
        app,
        host=params.host,
        port=params.port,
        workers=1
    )


if __name__ == '__main__':
    run_api()
