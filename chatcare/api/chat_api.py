# coding=utf-8
from fastapi import HTTPException

from chatcare.utils.types import *
from chatcare.api.chat_llm import chat_llm, load_llm_model
from chatcare.api.chat_search_engine import chat_search_engine
from chatcare.config import params


async def list_models():
    """获取所有llm列表"""
    global model_args
    model_card = ModelCard(id=params.llm_model_name)
    return ModelList(data=[model_card])


async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """ChatCare对话接口"""
    if params.chat_mode == "se":
        chat_completions_api = chat_direct_with_search_engine
    elif params.chat_mode == "llm":
        chat_completions_api = chat_direct_with_llm
    else:
        chat_completions_api = chat_with_knowledge_base
    try:
        return await chat_completions_api(request)
    except:
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content="很抱歉，请重新问我一次！"),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_direct_with_llm(request: ChatCompletionRequest):
    """直接与LLM对话，暂不支持历史、多轮对话"""
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
    if 'infer' not in globals():
        model, tokenizer, infer = load_llm_model(params)
    content = await chat_llm(query, history=history)
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=content),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_direct_with_search_engine(request: ChatCompletionRequest):
    """
    直接与向量数据库对话，暂不支持历史、多轮对话
    """
    # 用户名默认为user
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    query = request.messages[-1].content
    content = await chat_search_engine(query)
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=content),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_with_knowledge_base(request: ChatCompletionRequest):
    """
    chat_with_knowledge_base
    """
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content="This API Has Not Implemented !!!"),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")
