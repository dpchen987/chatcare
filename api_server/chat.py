# coding=utf-8


from utils.types import *
from utils.logger import logger
from config import params
from sse_starlette.sse import ServerSentEvent, EventSourceResponse


# ------------------------------- chat by embeddings ----------------------------------------#
async def chat_vs(query: str, history: List[List[str]]):
    raise NotImplementedError


# ------------------------------- chat by llm ----------------------------------------#

def load_llm_model(params):
    """ 载入不同llm模型用 """
    llm_model_name, llm_checkpoint_dir = params.llm_model_name, params.llm_checkpoint_dir
    device_map = "cpu" if params.device == "cpu" else "auto"
    model, tokenizer, infer = None, None, None
    if llm_model_name == "baichuan7b":
        from llms.baichuan7b import load_model, infer
        raise NotImplementedError
    elif llm_model_name == "qwen":
        from llms.qwen import load_model, infer
        raise NotImplementedError
    elif llm_model_name == "baichuan13b":
        from llms.baichuan13b import load_model, infer
        model = load_model(params.llm_checkpoint_dir, device_map)
    else:
        from llms.chatglm2_6b import load_model, infer
        model, tokenizer = load_model(params.llm_checkpoint_dir, device_map)

    if params.debug:
        logger.info(
            f"Load model successful! || llm_model_name: {llm_model_name} || llm_checkpoint_dir: {llm_checkpoint_dir} || type: {type(model)}")
    return model, tokenizer, infer


if params.chat_mode == "llm":
    model, tokenizer, infer = load_llm_model(params)


async def chat_llm(query: str, history: List[List[str]]) -> str:
    """
    llm单次推理，非流式
    :param query:
    :param history:
    :return:
    """
    time_start = time.time()
    global model, tokenizer, infer
    if params.llm_model_name == "baichuan13b":
        content = infer(model, query, history)
    else:
        content = infer(model, tokenizer, query, history)
    content = content.strip()
    if params.debug:
        logger.info(
            f"Infer successfully! || Cost_time(s): {time.time() - time_start} || Query: {query} || Response: {content}")
    return content


async def chat_llm_stream(query: str, history: List[List[str]]):
    """
    llm流式推理
    :param query:
    :param history:
    :return:
    """
    raise NotImplementedError


async def predict(query: str, history: List[List[str]], model_id: str):
    """ offical code  """
    global model, tokenizer

    choice_data = ChatCompletionResponseStreamChoice(
        index=0,
        delta=DeltaMessage(role="assistant"),
        finish_reason=None
    )
    chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
    yield "{}".format(chunk.model_dump_json(exclude_unset=True))

    current_length = 0

    for new_response in model.chat_stream(tokenizer, query, history):
        if len(new_response) == current_length:
            continue

        new_text = new_response[current_length:]
        current_length = len(new_response)

        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content=new_text),
            finish_reason=None
        )
        chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
        yield "{}".format(chunk.model_dump_json(exclude_unset=True))

    choice_data = ChatCompletionResponseStreamChoice(
        index=0,
        delta=DeltaMessage(),
        finish_reason="stop"
    )
    chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
    yield "{}".format(chunk.model_dump_json(exclude_unset=True))
    yield '[DONE]'
