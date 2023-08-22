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
    response, history = model.chat(tokenizer, query, history=history)
    return response


def infer_stream():
    """
    流式推理
    :return:
    """
    raise NotImplementedError


if __name__ == '__main__':
    checkpoint_path = r'/home/junjie/data/model/modelscope/chatglm2-6b-int4'
    model, tokenizer = load_model(checkpoint_path, device='cpu')
    print('-' * 88)
    response = infer(model, tokenizer, "上海颐家是什么？")
    print(response)
