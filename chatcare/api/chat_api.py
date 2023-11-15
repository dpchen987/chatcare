# coding=utf-8
from fastapi import HTTPException, Request, Response, Cookie
from fastapi.responses import StreamingResponse
import uuid
from chatcare.utils.types import *
from chatcare.utils.logger import logger
from chatcare.api.chat_llm import load_llm_model, chat_llm, chat_llm_stream
from chatcare.api.chat_vector_search import chat_vector_search, chat_vector_search_stream, chat_match_search
from chatcare.config import params
from typing_extensions import Annotated

async def list_models():
    """获取所有llm列表"""
    global model_args
    model_card = ModelCard(id=params.llm_model_name)
    return ModelList(data=[model_card])


async def chat_multi_turn(request: ChatKnowledgeBaseRequest, response: Response, chat_id: Annotated[Union[str, None], Cookie()] = None) -> ChatCompletionResponse:
    """ChatCare对话接口"""
    # chat id check
    if not chat_id:
        chat_id = str(uuid.uuid4())
        logger.info(f"---create a new chatid:{chat_id} ~---")
    logger.info(f"---chatid :{chat_id} ~---")
    response.set_cookie(key='chat_id', value=chat_id)
    if params.chat_mode == "vs":
        chat_completions_api = chat_direct_with_search_engine
    elif params.chat_mode == "llm":
        chat_completions_api = chat_direct_with_llm
    else:
        chat_completions_api = chat_with_knowledge_base_mult
    try:
        return await chat_completions_api(request, chat_id)
    except:
        logger.exception('An error occurred in api: `/v1/chat/completions`!')
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content="很抱歉，请重新问我一次！"),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """ChatCare对话接口"""
    if params.chat_mode == "vs":
        chat_completions_api = chat_direct_with_search_engine
    elif params.chat_mode == "llm":
        chat_completions_api = chat_direct_with_llm
    else:
        chat_completions_api = chat_with_knowledge_base
    try:
        return await chat_completions_api(request)
    except:
        logger.exception('An error occurred in api: `/v1/chat/completions`!')
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content="很抱歉，请重新问我一次！"),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_stream_search_engine_generator(query: str, history: List[List[str]] = None):
    async for chunk in chat_vector_search_stream(query, history):
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=chunk),
            finish_reason="stop"
        )
        chunk = ChatCompletionResponse(model="se_stream", choices=[choice_data], object="chat.completion")
        yield f"data: {chunk.json(exclude_unset=True, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def chat_direct_with_search_engine(request: ChatCompletionRequest):
    """
    直接与向量数据库对话，暂不支持历史、多轮对话
    """
    # 用户名默认为user
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    query = request.messages[-1].content
    if request.stream:
        return StreamingResponse(chat_stream_search_engine_generator(query), media_type="text/event-stream")
    content = await chat_vector_search(query)
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=content),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_stream_llm_generator(query: str, history: List[List[str]] = None):
    async for chunk in chat_llm_stream(query, history):
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=chunk),
            finish_reason="stop"
        )
        chunk = ChatCompletionResponse(model="llm_stream", choices=[choice_data], object="chat.completion")
        yield f"data: {chunk.json(exclude_unset=True, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def chat_direct_with_llm(request: ChatCompletionRequest):
    """直接与LLM对话，暂不支持历史、多轮对话"""
    global model, tokenizer, infer, infer_stream
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
    if 'infer' not in globals():
        model, tokenizer, infer, infer_stream = load_llm_model(params)
    if request.stream:
        return StreamingResponse(chat_stream_llm_generator(query, history), media_type="text/event-stream")
    content = await chat_llm(query, history=history)
    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=content),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


async def chat_with_knowledge_base(request: Request, chat_request: ChatKnowledgeBaseRequest):
    """
    chat_with_knowledge_base
    """
    response_chat_with_knowledge_base = ChatKnowledgeBaseResponse()
    try:
        chat_id = request.cookies['chat_id']
        chat_request.chat_id = chat_id
        response_chat_with_knowledge_base.chat_id = chat_id
        query = chat_request.messages[-1].content
        # Todo 根据chat_id拉取history
        history = None
        answer = await chat_vector_search(query, history)
        if isinstance(answer, Dict):
            response_chat_with_knowledge_base.summary = answer['summary']
            response_chat_with_knowledge_base.details = answer['details']

        elif isinstance(answer, str):
            response_chat_with_knowledge_base.error = 1
            response_chat_with_knowledge_base.summary = f'您的提问<{query}>异常，请问我护理相关问题！'

    except:
        logger.exception('An error occurred in api: `chat_with_knowledge_base`!')
        response_chat_with_knowledge_base.error = 2
        response_chat_with_knowledge_base.summary = f'发生错误，请再问我一次！'

    return response_chat_with_knowledge_base

async def chat_with_knowledge_base_mult(chat_request: ChatKnowledgeBaseRequest, chat_id):
    """
    chat_with_knowledge_base request, chat_id
    """
    response_chat_with_knowledge_base = ChatKnowledgeBaseResponse()
    try:
        query = chat_request.messages[-1].content
        answer = await chat_match_search(query, chat_id)
        if isinstance(answer, Dict):
            response_chat_with_knowledge_base.summary = answer['summary']
            response_chat_with_knowledge_base.intent_id = answer['intent_id']
            response_chat_with_knowledge_base.hints = answer['hints']
            response_chat_with_knowledge_base.details = answer['details']

        elif isinstance(answer, str):
            response_chat_with_knowledge_base.error = 1
            response_chat_with_knowledge_base.summary = f'您的提问<{query}>异常，请问我护理相关问题！'

    except:
        logger.exception('An error occurred in api: `chat_with_knowledge_base`!')
        response_chat_with_knowledge_base.error = 2
        response_chat_with_knowledge_base.summary = f'发生错误，请再问我一次！'

    return response_chat_with_knowledge_base
