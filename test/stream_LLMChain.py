from langchain import  LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.tongyi import Tongyi
from langchain.callbacks.base import BaseCallbackHandler

# 定义自定义的回调处理器，用于处理流式输出的每个token
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


# 初始化OpenAI的LLM（语言模型），开启流式输出
# llm = OpenAI(temperature=0.7, streaming=True)
llm = Tongyi(temperature=0,
             streaming=True)
llm.model_name = "qwen-turbo"

# 定义PromptTemplate，指定输入的格式
prompt_template = PromptTemplate(
    input_variables=["question", "chat_history"],
    template=(
        "You are a helpful assistant. You have the following conversation history:\n"
        "{chat_history}\n"
        "Based on this, answer the following question: {question}"
    )
)

# 创建会话记忆，使用 ConversationBufferMemory 存储会话历史
memory = ConversationBufferMemory(memory_key="chat_history")
# 自定义回调处理器
callback_handler = MyCustomCallbackHandler()

# 将 LLM 和 PromptTemplate 结合到 LLMChain 中，同时加入 Memory 功能
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=memory,
)
tools = []
# agent
# agent = initialize_agent(
#                 tools=tools,
#                 llm=llm_chain,
#                 agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
#                 memory=memory,
#                 verbose=True,
#                 # prompt=prompt_template,
# )
# 创建生成器函数，流式生成回答
def stream_answer_with_memory(question):
    # 使用 .stream 方法进行流式生成，带有记忆功能
    response_generator = llm_chain.run({"question": question}, callbacks=[callback_handler])
    # print(agent)
    # agent.invoke(input=question, callbacks=[callback_handler])

# 提出多个问题，并测试会话记忆功能
question_1 = "你好，今天星期几？"
stream_answer_with_memory(question_1)

# 假设用户提了一个后续问题
print("\n")  # 打印换行，表示新问题的开始
question_2 = "中华人民共和国的伟大导师是谁?"
stream_answer_with_memory(question_2)
