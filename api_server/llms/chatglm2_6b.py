from transformers import AutoTokenizer, AutoModel


def load_model(checkpoint_path, device_map="cuda"):
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True).half().to(device_map)
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
    model, tokenizer = load_model(checkpoint_path)
    print('-' * 88)
    response = infer(model, tokenizer, "上海颐家是什么？")
    print(response)
