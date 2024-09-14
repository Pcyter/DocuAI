import json
import base64
import hashlib
import math
import uuid
import time
from datetime import datetime
import time
import requests
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
# from langchain_community.llms.tongyi import Tongyi
# from langchain_community.chat_models.openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_community.callbacks import StreamlitCallbackHandler

from template import MODEL_DIALOG_TEMPLATE

# LLM model
# openai_base_url
# openai_base_url = "http://117.132.181.235:9050/nxmobilev1"
openai_base_url = "http://10.250.198.16:9050/nxmobilev1"

# model_name = "qwen-api"
model_name = "Qwen1.5-14B-Chat"

# db model
# model_db = "oracle"
model_db = "mysql"

mysql_db_user = "root"
mysql_db_pass = "123456"
mysql_db_host = "localhost"
mysql_db_port = 3306
mysql_db_name = "test_db"

ora_db_user = "reward_web"
ora_db_pass = "BtGBtp_1230"
ora_db_host = "10.236.204.12"
ora_db_port = 1566
ora_db_name = "REWARD_WEB"

redis_db_host = "10.236.157.40"
redis_db_port = "6379"
redis_db_pass = "Newland@10086"

# redis_db_host = "localhost"
# redis_db_port = "6379"
# redis_db_pass = "foobared"

# 知识库管理权限编码
knowledge_manager_role = '100300'
class Http_Param(object):
    # 初始化
    def __init__(self, URL, APPID, APPKey):
        self.URL = URL
        self.APPID = APPID
        self.APPKey = APPKey

    # 生成url
    def create_header(self):
        appid = self.APPID
        appKey = self.APPKey
        uuid = getUUID()
        # 24 + 32 + 8
        appName = self.URL.split('/')[3]
        for i in range(24 - len(appName)):
            appName += "0"
        capabilityname = appName
        # print(len(capabilityname))
        csid = appid + capabilityname + uuid
        tmp_xServerParam = {
            "appid": appid,
            "csid": csid
        }
        xCurTime = str(math.floor(time.time()))
        xServerParam = str(base64.b64encode(json.dumps(tmp_xServerParam).encode('utf-8')), encoding="utf8")
        # turn to bytes
        xCheckSum = hashlib.md5(bytes(appKey + xCurTime + xServerParam, encoding="utf8")).hexdigest()

        header = {
            "appKey": appKey,
            "X-Server-Param": xServerParam,
            "X-CurTime": xCurTime,
            "X-CheckSum": xCheckSum,
            "content-type": "application/json"
        }

        return header


def getUUID():
    return "".join(str(uuid.uuid4()).split("-"))

def getChainLLM(use_stream: bool=False,app="/chat/completions",
                openai_base_url="http://10.250.198.16:9050/nxmobilev1"):

    httpParam = Http_Param(URL=f"{openai_base_url}{app}", APPID='chatbiid', APPKey='3fac9780bfca3e442598bfed408f3cc8')
    httpHeader = httpParam.create_header()

    # OpenAI 模式
    llm = ChatOpenAI(
                    streaming=use_stream,
                    openai_api_key="EMPTY",
                    base_url=f"{openai_base_url}",
                    model_name=f"{model_name}",
                    temperature=0,
                    default_headers=httpHeader,
                    max_tokens=1000,
                    callbacks=[StreamingStdOutCallbackHandler()],
    )


    # llm = Tongyi(temperature=0, streaming=True)
    # llm.model_name = "qwen-max"
    # print(llm)

    return llm

def getLLM(use_stream: bool=False,model_name="qwen-turbo", api_key=""):

    # llm = Tongyi(api_key=api_key,
    #              temperature=0,
    #              streaming=use_stream)
    # llm.model_name = model_name

    # OpenAI 模式
    llm = ChatOpenAI(
        streaming=use_stream,
        openai_api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name=f"{model_name}",
        temperature=0,
        max_tokens=1000,
        callbacks=[StreamingStdOutCallbackHandler()]
    )

    return llm

def request_chat(query,api_base_url: str=openai_base_url,app: str="/chat/completions",postdata = ""):
    time1 = datetime.now()
    # 测试时候在此处正确填写相关信息即可运行
    # 能力接口鉴权信息
    # APPKEY为推理平台->API网关->授权管理->应用秘钥
    # APPID为推理平台->API网关->授权管理->应用标识
    # ws协议URL由：ws://HOST:PORT/ws/api_path
    # http协议URL由：http://HOST:PORT/api_path
    # HOST为你所在网络与AI平台的接口机IP，例如外网接口IP地址：117.132.181.235；哈池内网接口ip：10.252.122.96；承载网接口ip：10.255.77.9
    # PORT为协议端口，http（9050）、ws（9070）、grpc（9080）
    # api_path为推理平台API网关中对应AI能力的PATH映射。
    # image_path为输入的图像信息，图像路径
    # httpParam = Http_Param(URL='http://117.132.181.235:9050/RecognitionForTimeProvincePhone',APPID='您的appid', APPKey='您的appkey')
    httpParam = Http_Param(URL=f"{api_base_url}{app}", APPID='chatbiid', APPKey='3fac9780bfca3e442598bfed408f3cc8')
    httpHeader = httpParam.create_header()
    if len(postdata) == 0:
        postdata = {
                    "model": f"{model_name}",
                    "messages": [{"role": "user", "content": f"{query}"}],
                    "temperature": 0.7
                }
    # 业务参数,更多参数可在接口查看,参数说明: [picData:待识别图片base64后的字符串]
    # image_path = 'test.jpg'
    # with open(image_path, 'rb') as f:
    #     images = f.read()
    #     imgStr = base64.b64encode(images)
    # #请求体参数根据自己本身能力参数提供
    # postdata = {"picData":str(imgStr,"utf-8")}
    body = json.dumps(postdata)
    # 开始处理
    response = requests.post(httpParam.URL, data=body, headers=httpHeader, timeout = None)
    data = response.json()

    # 识别结果解析
    status_code = response.status_code
    if status_code != 200:
        # 鉴权失败
        print("Http请求失败，状态码：" + str(status_code) + "，错误信息：" + response.text)
    else:
        # 鉴权成功
        # respData = json.loads(strjson)
        content = data['choices'][0]["message"]["content"]
        #
        print(content)
    #     if error_code != 0:
    #         print("业务请求失败，状态码：" + str(error_code) + "，错误信息：" + respData['errorMsg'])
    #     else:
    #         print(respData['result'])

    time2 = datetime.now()
    print(time2 - time1)


if __name__ == "__main__":
    # data = {
    #     "query": "什么是家宽结算积分规则",
    #     "knowledge_base_name": "samples",
    #     "top_k": 3,
    #     "score_threshold": 1,
    #     "history": [],
    #     "stream": False,
    #     "model_name": "Qwen1.5-14B-Chat",
    #     "temperature": 0.7,
    #     "max_tokens": 0,
    #     "prompt_name": "default"
    # }
    # request_chat("什么是渠道积分规则", api_base_url="http://117.132.181.235:9050", app="/v5/chat/knowledge_base_chat",
    #              postdata=data)
    # 获取当前使用的模型token限制
    # llm = getChainLLM()
    llm = getLLM(use_stream=False,model_name="qwen-turbo", api_key="sk-d882cf19ce74419c9af1d20586d4d96b")
    prompt = PromptTemplate.from_template(MODEL_DIALOG_TEMPLATE)
    mem = ConversationBufferWindowMemory(memory_key="history", return_messages=True, k=2)

    chain = prompt | llm
    # chain = LLMChain(prompt=prompt,
    #          llm=llm,
    #          memory=mem,
    #          verbose=False,
    #          output_parser=StrOutputParser(),
    #          # callbacks=[StreamingStdOutCallbackHandler()],
    #
    #          )
    # st_callback = StreamlitCallbackHandler()

    # response = chain.stream({"input":"你好"}, callbacks=[st_callback])
    # response = chain.stream({"question":"你好，今天几号"})
    history = []

    response = chain.stream({"question":"你好，老张是我的好朋友。", "history":history})
    history.append("question:你好，老张是我的好朋友？")
    msg = ""
    for chunk in response:
        if chunk:
            msg += chunk.content
            print(chunk.content)
            print(chunk)
    history.append(f"answer::{msg}")
    print(chain)
    response = chain.stream({"question":"老张是谁？", "history":history})
    history.append("question:老张是谁？")
    for chunk in response:
        if chunk:
            print(chunk.content)

    print(chain)
    # max_tokens = response.response_metadata["token_usage"]["total_tokens"]
    # print(f"Maximum tokens: {max_tokens}")
