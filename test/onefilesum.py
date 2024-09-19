from docx import Document
from langchain_community.llms.tongyi import Tongyi
from langchain import LLMChain, PromptTemplate


# 1. 解析 docx 文档
def parse_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)


# 2. 使用 Tongyi 模型进行文档解析
def process_document(file_path):
    # 解析文档内容
    document_text = parse_docx(file_path)

    # 创建 Tongyi 模型实例
    llm = Tongyi(temperature=0, streaming=True)
    llm.model_name = "qwen-turbo"

    # 定义 PromptTemplate 和 LLMChain
    template = """Given the following document, answer the question and provide a summary.

    Document: {document}

    Question: {question}

    Summary:
    """
    prompt = PromptTemplate(template=template, input_variables=["document", "question"])
    chain = prompt | llm

    # 示例问题
    question = "这个文档的主要内容是什么?"

    # 使用 LLMChain 解析文档
    output = chain.invoke({"document": document_text, "question": question})
    # 5. 输出结果
    print("Generated Summary and Answer:\n", output)

    while True:
        question = input("\n请输入问题: ")
        # 使用 LLMChain 解析文档
        output = chain.invoke({"document": document_text, "question": question})
        # 5. 输出结果
        print("问题答案:\n", output)






if __name__ == "__main__":
    # 3. 指定要解析的 docx 文件路径
    file_path = "../docx/AI诊断截屏数据分析汇总需求文档_陈澍.docx"

    # 4. 解析并处理文档
    process_document(file_path)

