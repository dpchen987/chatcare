# coding=utf-8
# 基于向量数据库的匹配问答

from chatcare.utils.types import *
from chatcare.utils.logger import logger
from chatcare.config import params
from chatcare.chains.chain import bge, chain


async def chat_search_engine(query: str, history: List[List[str]] = None):
    time_start = time.time()
    content = chain(query)
    content = content.strip()
    if params.debug:
        logger.info(
            f"Chat with search engine successfully! || Cost_time(s): {time.time() - time_start} || Query: {query} || Content: {content}")
    return content


if __name__ == '__main__':
    content = chat_search_engine(query="肺炎需要注意什么？")
    print(content)
