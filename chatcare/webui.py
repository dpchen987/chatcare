# coding=utf-8

import gradio as gr

from chatcare.api.chat_llm import chat_llm


async def chat(query: str, chat_history: list):
    """
    导入chat-func
    """
    response = await chat_llm(query, None)
    chat_history.append((query, response))
    return "", chat_history


async def chat_stream(input, history):
    """流式回答"""
    # history.append({"role": "user", "content": input})
    # history.append({"role": "assistant", "content": response})
    # messages = [(history[i]["content"], history[i + 1]["content"]) for i in range(0, len(history) - 1, 2)]
    raise NotImplementedError


def main():
    with gr.Blocks() as app:
        gr.Markdown(
            '# <center> ChatCare v0.1 推理服务 \n'
            '<div align="center"><img src="https://www.day-care.cn/wp-content/themes/yijia/assets/images/LOGO-min.png" alt="logo"></div>\n'
        )
        chatbot = gr.Chatbot()
        tb_input = gr.Textbox(
            label="请输入内容：", value="上海颐家是什么?",
            placeholder="输入问题后，回车开始生成！"
        ).style(container=False)
        tb_input.submit(chat, [tb_input, chatbot], [tb_input, chatbot])

    app.launch(server_name="0.0.0.0", server_port=8001, share=True)


if __name__ == '__main__':
    main()