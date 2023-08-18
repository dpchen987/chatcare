# coding=utf-8
# 开发测试用

from transformers import AutoTokenizer, AutoModelForCausalLM


def load_model(checkpoint_path, device_map="auto"):
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        device_map=device_map,
        trust_remote_code=True,
        resume_download=True,
    ).eval()

    tokenizer = AutoTokenizer.from_pretrained(
        checkpoint_path,
        trust_remote_code=True,
        resume_download=True,
    )
    return model, tokenizer


def infer(model, tokenizer, query: str, history: list = None):
    if history:
        raise NotImplementedError
    input_ids = tokenizer.encode(query, return_tensors="pt").to(model.device)
    output_ids = model.generate(input_ids, max_length=1000, num_beams=1)
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return response


def infer_stream():
    """
    流式推理
    :return:
    """
    raise NotImplementedError


if __name__ == '__main__':
    checkpoint_path = "/aidata/junjie/data/model/huggingface/TinyStories-33M"
    model, tokenizer = load_model(checkpoint_path)
    response = infer(model, tokenizer, "hello")
    print('-' * 88)
    print(response)
