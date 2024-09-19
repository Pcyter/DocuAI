# 定义自定义的回调处理器，用于处理流式输出的每个token
from langchain_core.callbacks import BaseCallbackHandler


class MyCustomCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        # 可以在初始化时设置一些需要记录的状态或数据
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """当LLM生成一个新token时调用的回调函数"""
        # 将生成的token保存到tokens列表
        self.tokens.append(token)
        # 输出token，模拟流式输出
        print(token, end='', flush=True)

    def on_llm_end(self, result, **kwargs) -> None:
        """在生成结束时调用的回调函数"""
        print("\nGeneration complete!")