# coding=utf-8

import gradio as gr

from server.chat.chat_llm import chat_llm


async def chat(input, history):
    """
    导入chat-func
    """
    response = await chat_llm(input, history)
    return response


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
        state = gr.State([])
        with gr.Row():
            tb_input = gr.Textbox(
                label="请输入内容：", value="上海颐家是什么?",
                placeholder="输入问题后，回车开始生成！"
            ).style(container=False)
        tb_output = gr.Textbox(label="输出内容：")
        tb_input.submit(chat, [tb_input, state], [tb_output])

    app.launch(server_name="0.0.0.0", server_port=8001, share=True)


if __name__ == '__main__':
    main()
