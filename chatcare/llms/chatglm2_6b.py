import time

from transformers import AutoTokenizer, AutoModel
from chatcare.utils.logger import logger


def load_model(checkpoint_path, device="cuda"):
    if device != "cuda":
        logger.error(f"ChatGLM2-6b-int4 is not allowed on {device=}!")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True).half().to(device)
    model = model.eval()
    return model, tokenizer


def infer(model, tokenizer, query: str, history: list = None, **kwargs):
    if history:
        raise NotImplementedError
    prompt_template = f'假设你现在是上海颐家医疗养老服务有限公司开发的医疗养老人工智能助手，名字叫颐小爱，你擅长为老年人提供养老和医疗护理、康复相关的建议，请回答下列问题"{query}"'
    content, history = model.chat(tokenizer, prompt_template, history=history, **kwargs)
    return content


def infer_stream(model, tokenizer, query: str, history: list = None, top_p: float = 1.0, temperature: float = 1.0,
                 **kwargs):
    """
    流式推理
    :return:
    """
    prompt_template = f'假设你现在是上海颐家医疗养老服务有限公司开发的医疗养老人工智能助手，名字叫颐小爱，你擅长为老年人提供养老和医疗护理、康复相关的建议，请回答下列问题"{query}"'
    for content, query_content in model.stream_chat(tokenizer, prompt_template, history, top_p=top_p,
                                                    temperature=temperature, **kwargs):
        yield content


if __name__ == '__main__':
    checkpoint_path = r'/workspace/models/chatglm2-6b-int4'
    model, tokenizer = load_model(checkpoint_path, device='cuda')
    print('direct', '-' * 88)
    content = infer(model, tokenizer, "上海颐家是什么？", top_p=2, temperature=1)
    print(content)

    # print('stream', '-' * 88)
    # for item in infer_stream(model, tokenizer, "上海颐家是什么？"):
    #     print(item, end='\r')
    #     time.sleep(0.01)
