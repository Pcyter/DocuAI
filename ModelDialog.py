import traceback

from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (QWidget, QPushButton, QLabel,
                               QLineEdit, QVBoxLayout, QHBoxLayout,
                               QMessageBox, QTextBrowser)
from langchain_core.prompts import PromptTemplate

from template import MODEL_DIALOG_TEMPLATE
from util import getChainLLM, getLLM


class ModelDialogWindow(QWidget):
    update_text_signal = Signal(str)  # 定义一个信号，当需要更新文本时发射

    def __init__(self):
        super().__init__()

        self.initUI()
        self.init_signal_slot()

    def initLLM(self,net,url,api_key,model):
        prompt = PromptTemplate.from_template(MODEL_DIALOG_TEMPLATE)

        if net == '内网':
            if len(url)>0 and "http" in url:
                llm = getChainLLM(use_stream=True, openai_base_url=url)
                self.chain = prompt | llm
        else:
            if len(api_key)>0 and len(model)>0:
                llm = getLLM(use_stream=True, api_key=api_key,model_name=model)
                self.chain = prompt | llm

    def initUI(self):
        self.setWindowTitle('大模型对话窗口')
        self.setGeometry(100, 100, 800, 600)

        # 创建布局
        layout = QVBoxLayout()

        # 输出显示
        self.web_view = QTextBrowser(self)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.web_view)

        # // 设置字体大小
        self.font = QFont()
        self.font.setPixelSize(14) #12号字体大小，你可以根据需要设置
        self.web_view.setFont(self.font)


        layout.addLayout(output_layout)

        # 创建输入框和发送按钮的布局
        send_layout = QHBoxLayout()

        # 对话输入
        self.dialog_entry = QLineEdit()
        self.dialog_entry.returnPressed.connect(self.send_dialog)
        self.dialog_entry.setFixedHeight(40)
        self.dialog_entry.setFont(self.font)
        # 发送按钮
        self.send_button = QPushButton('发送')
        self.send_button.clicked.connect(self.send_dialog)
        send_layout.addWidget(self.dialog_entry)
        send_layout.addWidget(self.send_button)

        layout.addLayout(send_layout)

        self.setLayout(layout)

        self.historys = []
        self.resp_list = []
        self.response = None
        self.markdown_text = ""


    def init_signal_slot(self):
        self.update_text_signal.connect(self.web_view.setMarkdown)  # 连接信号到槽
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)  # 定时器超时连接更新文本的槽
        self.timer.start(10)  # 定时器开始，每1000毫秒触发一次


    @Slot(str)
    def update_text(self):
        if self.response is not None:
            try:
                chunk = next(self.response)
                self.resp_list.append(chunk.content)
                # 发射信号
                self.update_text_signal.emit(self.markdown_text + "\n" + "".join(self.resp_list))
                self.historys.append("".join(self.resp_list))

                # 滚动到最下面
                cursor = self.web_view.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.web_view.setTextCursor(cursor)

            except StopIteration:
                # print("没有更多的信息了")
                self.resp_list.clear()
            except Exception as e:
                self.resp_list.clear()
                print(f"Error : {e}")
                traceback.print_exc()


    def send_dialog(self):
        dialog_text = self.dialog_entry.text()
        self.historys.append(f"\n question:{dialog_text}")
        self.historys.append(f"\n answer:")
        try:
            self.response = self.chain.stream({"question":dialog_text,"history":self.historys})
            self.dialog_entry.setText("")
            self.web_view.append(f"😜：{dialog_text}")
            self.web_view.append("".join("🤖："))  # 发射信号
            self.markdown_text = self.web_view.toHtml()

        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))