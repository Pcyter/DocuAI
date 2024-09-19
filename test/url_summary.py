from langchain_community.llms.tongyi import Tongyi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate




# summary chain:对每个url输出进行总结
def summary(product, content):
    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")
    llm = Tongyi(temperature=0,
                 streaming=True)
    llm.model_name = "qwen-turbo"


    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])
    map_prompt = """
        content is :{text}
        Please summarize the Chinese manufacturers of """ + product + """ ,based on the above content and return them in list format.
        The returned results should be in the following format(Return strictly in list format.): ["manu1","manu2","manu3"...]
        The manufacturers should be from the Chinese market, and it's preferred to use the full name of the manufacturers rather than abbreviations.
        """
    combine_prompt = """
        content is :{text}
        Please summarize the Chinese manufacturers of """ + product + """ ,based on the above content and return them in list format.
        The returned results should be in the following format(Return strictly in list format.): ["manu1","manu2","manu3"...]
        The manufacturers should be from the Chinese market, and it's preferred to use the full name of the manufacturers rather than abbreviations.
        """
    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text"])
    combine_prompt_template = PromptTemplate(
        template=combine_prompt, input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=combine_prompt_template,
        verbose=False
    )

    output = summary_chain.run(input_documents=docs, )
    # print(output)
    return output


print(summary("GPU","GPU的生产厂家有：七彩虹厂商,技嘉厂商."))
print(type(summary("GPU","GPU的生产厂家有：七彩虹厂商,技嘉厂商.")))
