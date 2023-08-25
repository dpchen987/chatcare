from transformers import AutoTokenizer, AutoModel
from chatcare.utils.logger import logger


def load_model(checkpoint_path, device="cuda"):
    if device != "cuda":
        logger.error(f"ChatGLM2-6b-int4 is not allowed on {device=}!")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True).half().to(device)
    model = model.eval()
    return model, tokenizer


def infer(model, tokenizer, query: str, history: list = None):
    if history:
        raise NotImplementedError
    prompt_template = f'假设你现在是上海颐家医疗养老服务有限公司开发的医疗养老人工智能助手，名字叫颐小爱，你擅长的领域是为老年人的养老和医疗护理的建议，请回答下列问题"{query}"'
    response, history = model.chat(tokenizer, prompt_template, history=history)
    return response


def infer_stream():
    """
    流式推理
    :return:
    """
    raise NotImplementedError


if __name__ == '__main__':
    checkpoint_path = r'/workspace/models/chatglm2-6b-int4'
    model, tokenizer = load_model(checkpoint_path, device='cuda')
    print('-' * 88)
    response = infer(model, tokenizer, "上海颐家是什么？")
    print(response)
