# coding=utf-8
# 基于向量数据库的匹配问答

from chatcare.utils.types import *
from chatcare.utils.logger import logger
from chatcare.config import params
from chatcare.chains.chain import chain
from chatcare.chains import chain_multi_turn


async def chat_multi_turn(query: str, history: List[List[str]] = None):
    time_start = time.time()
    content = chain_multi_turn.chain(query)
    if isinstance(content, str):
        content = content.strip()
    if params.debug:
        logger.info(
            f"Chat with vector search successfully! || Cost_time(s): {time.time() - time_start} || Query: {query} || Content: {content}")
    return content

async def chat_vector_search(query: str, history: List[List[str]] = None):
    time_start = time.time()
    content = chain(query)
    if isinstance(content, str):
        content = content.strip()
    if params.debug:
        logger.info(
            f"Chat with vector search successfully! || Cost_time(s): {time.time() - time_start} || Query: {query} || Content: {content}")
    return content


async def chat_vector_search_stream(query: str, history: List[List[str]] = None):
    time_start = time.time()
    content = chain(query)
    content = content.strip()
    for chunk in content:
        yield chunk
    if params.debug:
        logger.info(
            f"Chat stream with vector search successfully! || Cost_time(s): {time.time() - time_start} || Query: {query} || Content: {content}")


if __name__ == '__main__':
    query = "肺炎需要注意什么？"
    content = chat_vector_search(query)
    print(content)
