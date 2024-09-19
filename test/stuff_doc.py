import os

from langchain_community.llms.tongyi import Tongyi
from langchain_core.prompts import ChatPromptTemplate

import ReadFile

# document = [
#     Document(page_content="苹果是红色的", metadata={"title": "apple_book"}),
#     Document(page_content="蓝莓是蓝色的", metadata={"title": "blueberry_book"}),
#     Document(page_content="香蕉是黄色的", metadata={"title": "banana_book"}),
# ]
documents = ReadFile.parse_file_documents(fr"E:\workspace\document_summary\requirement.txt")
from langchain.chains import LLMChain, StuffDocumentsChain
from langchain_core.prompts import PromptTemplate

# llm = ChatOpenAI(model="gpt-3.5-turbo")
llm = Tongyi(template= 0, model_name="qwen-turbo")
#
# document_prompt = PromptTemplate(
#     input_variables=["page_content"], template="{page_content}"
# )
# document_variable_name = "context"
# prompt = ChatPromptTemplate.from_template("总结这些内容: {context}")
#
# llm_chain = LLMChain(llm=llm, prompt=prompt)
# stuff_chain = StuffDocumentsChain(
#     llm_chain=llm_chain,
#     document_prompt=document_prompt,
#     document_variable_name=document_variable_name,
# )
#
# result = stuff_chain.invoke(documents)
# print(result["output_text"])


from langchain.chains.combine_documents import create_stuff_documents_chain

# llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_template("回答用户问题:\n question：{question} \n context: {context} \n history:{{history}}\n answer: ")
new_stuff_chain = create_stuff_documents_chain(llm = llm, prompt=prompt)
result = new_stuff_chain.stream({"question":"对文档进行总结","context": documents})
for chunk in result:
    print(chunk)


