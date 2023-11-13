# coding=utf-8
# Implements API for chatcare in OpenAI's format. (https://platform.openai.com/docs/api-reference/chat)
# Usage: python api.py
# code ref: https://github.com/QwenLM/Qwen-7B/blob/main/openai_api.py
# Visit http://localhost:8000/docs (default) for documents.

import os
import uuid
import torch
import uvicorn
from fastapi import FastAPI, Cookie, Request, Response, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from typing_extensions import Annotated
from typing import Union

from chatcare.utils.types import *
from chatcare import __version__
from chatcare.config import params
from chatcare.api.chat_api import (
    list_models, chat_completions, chat_direct_with_llm,
    chat_direct_with_search_engine,
    chat_with_knowledge_base, chat_multi_turn
)
from chatcare.api.knowledge_base_api import (
    list_kbs, create_kb, delete_kb
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def create_app():
    app = FastAPI(
        title="ChatCare API Server",
        version=__version__,
        lifespan=lifespan,
        root_path=params.root_path,
    )
    app.mount("/static", StaticFiles(directory="/workspace/knowledge_base/"), name="static")
    # pkg_dir = os.path.dirname(os.path.abspath(__file__)) /home/dapeng/chatcare-1/chatcare/login.html
    pkg_dir = '/workspace/knowledge_base/html/'
    html_path = os.path.join(pkg_dir, 'chat.html')
    login_path = os.path.join(pkg_dir, 'login.html')
    root_path = params.root_path

    @app.get('/root_path')
    async def get_rp(request: Request):
        return {'root_path': request.scope.get('root_path')}

    @app.get('/', response_class=HTMLResponse)
    async def home(user_id: Annotated[Union[str, None], Cookie()] = None):
        print(f'{user_id = }')
        if user_id != 'whoami':
            rd = '/login' if not root_path else f'/{root_path}/login'
            print(f'{rd = }')
            return RedirectResponse(rd, status_code=303)
        with open(html_path) as f:
            html = f.read()
        return html

    @app.get('/login', response_class=HTMLResponse)
    async def login():
        with open(login_path) as f:
            html = f.read()
        return html

    @app.post('/login2')
    async def loginpost(user: Annotated[str, Form()], password: Annotated[str, Form()]):
        print(f'{user = }, {password = }')
        if user == 'ailab' and password == 'cHat*&$AI':
            rd = '/' if not root_path else f'/{root_path}/'
            resp = RedirectResponse(rd, status_code=303)
            resp.set_cookie(key="user_id", value="whoami")
            # resp.set_cookie(key='chat_id', value=str(uuid.uuid4()))
            return resp
        rd = '/login' if not root_path else f'/{root_path}/login'
        return RedirectResponse(rd, status_code=303)

    @app.get('/logout')
    async def logout():
        rd = '/login' if not root_path else f'/{root_path}/login'
        resp = RedirectResponse(rd, status_code=303)
        resp.delete_cookie('user_id')
        return resp

    # 跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Tag: Chat
    app.get(
        "/v1/models",
        tags=["Chat"],
        summary="可用llm模型列表",
        response_model=ModelList
    )(list_models)

    app.post(
        "/v1/chat/multi_turn",
        tags=["Chat"],
        summary="ChatCare对话主接口",
        response_model=ChatKnowledgeBaseResponse
    )(chat_multi_turn)

    app.post(
        "/v1/chat/completions",
        tags=["Chat"],
        summary="ChatCare对话主接口",
        response_model=ChatCompletionResponse
    )(chat_completions)

    app.post(
        "/v1/chat/knowledge_base",
        tags=["Chat"],
        summary="与知识库对话",
        response_model=ChatKnowledgeBaseResponse
    )(chat_with_knowledge_base)

    app.post(
        "/v1/chat/vector_search",
        tags=["Chat"],
        summary="(DEV) 直接与 QA vector searcher 对话",
        response_model=ChatCompletionResponse
    )(chat_direct_with_search_engine)

    app.post(
        "/v1/chat/llm",
        tags=["Chat"],
        summary="(DEV) 直接与 LLM 对话",
        response_model=ChatCompletionResponse
    )(chat_direct_with_llm)

    # Tag: Knowledge Base Management
    app.get("/knowledge_base/list_knowledge_bases",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库列表")(list_kbs)

    app.post("/knowledge_base/create_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="创建知识库"
             )(create_kb)

    app.post("/knowledge_base/delete_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库"
             )(delete_kb)

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
