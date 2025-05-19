import os
from volcenginesdkarkruntime import Ark

# 初始化 Ark 客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

# 初始化对话历史
messages = [
    {"role": "system", "content": "你是人工智能助手。"}
]

print("----- 对话开始，输入 'exit' 退出 -----")

while True:
    # 获取用户输入
    user_input = input("你: ")
    
    # 如果输入 "exit" 则退出
    if user_input.lower() == "exit":
        print("对话结束。")
        break
    
    # 添加用户消息到历史
    messages.append({"role": "user", "content": user_input})
    
    # 发送请求（流式）
    print("AI: ", end="", flush=True)
    stream = client.chat.completions.create(
        model="doubao-1-5-thinking-pro-250415",
        messages=messages,
        stream=True,
    )
    
    # 处理流式响应
    full_response = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    # 把 AI 回复加入历史
    messages.append({"role": "assistant", "content": full_response})
    print("\n")