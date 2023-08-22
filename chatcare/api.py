# coding=utf-8
# Implements API for chatcare in OpenAI's format. (https://platform.openai.com/docs/api-reference/chat)
# Usage: python api.py
# code ref: https://github.com/QwenLM/Qwen-7B/blob/main/openai_api.py
# Visit http://localhost:8000/docs (default) for documents.

import torch
import uvicorn
from argparse import ArgumentParser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from chatcare.utils.types import *
from chatcare.utils import __version__
from chatcare.api.chat_api import (
    list_models, chat_direct_with_llm,
    chat_direct_with_search_engine,
    chat_with_knowledge_base
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
    )
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
        "/v1/chat/completions",
        tags=["Chat"],
        summary="直接与 LLM 对话",
        response_model=ChatCompletionResponse
    )(chat_direct_with_llm)

    app.post(
        "/v1/chat/search_engine",
        tags=["Chat"],
        summary="直接与 Search Engine 对话",
        response_model=ChatCompletionResponse
    )(chat_direct_with_search_engine)

    app.post(
        "/v1/chat/knowledge_base",
        tags=["Chat"],
        summary="与知识库对话",
        response_model=ChatCompletionResponse
    )(chat_with_knowledge_base)

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


def run_api(host, port, **kwargs):
    uvicorn.run(
        app,
        host=host,
        port=port,
    )
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Demo server port.")
    parser.add_argument("-u", "--uri", type=str, default="0.0.0.0",
                        help="Demo server name.")
    args = parser.parse_args()
    run_api(host=args.uri, port=args.port, workers=1)
