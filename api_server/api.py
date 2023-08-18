# coding=utf-8
# Implements API for chatcare in OpenAI's format. (https://platform.openai.com/docs/api-reference/chat)
# Usage: python api.py
# code ref: https://github.com/QwenLM/Qwen-7B/blob/main/openai_api.py
# Visit http://localhost:8000/docs (default) for documents.

import torch
import uvicorn
import os
from argparse import ArgumentParser
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from utils.types import *
from utils.logger import logger
from config import params
from chat import chat_llm


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    """获取所有llm列表"""
    global model_args
    model_card = ModelCard(id=os.path.basename(params.llm_model))
    return ModelList(data=[model_card])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    query = request.messages[-1].content
    prev_messages = request.messages[:-1]
    # Temporarily, the system role does not work as expected. We advise that you write the setups for role-play in your query.
    # if len(prev_messages) > 0 and prev_messages[0].role == "system":
    #     query = prev_messages.pop(0).content + query
    history = []
    if len(prev_messages) % 2 == 0:
        for i in range(0, len(prev_messages), 2):
            if prev_messages[i].role == "user" and prev_messages[i + 1].role == "assistant":
                history.append([prev_messages[i].content, prev_messages[i + 1].content])
            else:
                raise HTTPException(status_code=400, detail="Invalid request.")
    else:
        raise HTTPException(status_code=400, detail="Invalid request.")
    # if request.stream:
    #     generate = predict(query, history, request.model)
    #     return EventSourceResponse(generate, media_type="text/event-stream")
    response = await chat_llm(query, history=history)
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=response),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Demo server port.")
    parser.add_argument("-u", "--uri", type=str, default="0.0.0.0",
                        help="Demo server name.")
    args = parser.parse_args()

    uvicorn.run(app, host=args.uri, port=args.port, workers=1)
