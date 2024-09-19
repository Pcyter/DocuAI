import configparser

from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor, QAction, QIcon
from PySide6.QtWidgets import (QWidget, QPushButton, QLabel,
                               QLineEdit, QFileDialog, QVBoxLayout, QHBoxLayout,
                               QMessageBox, QTextBrowser, QMenuBar, QMenu)
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
import chardet

from ReadFile import parse_file, get_token_count, TOKEN_LIMIT, split_text_into_chunks, parse_file_documents
from template import FILE_DIALOG_TEMPLATE
from util import openai_base_url, getChainLLM, getLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
import logging
import traceback
from logging.config import fileConfig

class FileDialogWindow(QWidget):
    update_text_signal = Signal(str)  # 定义一个信号，当需要更新文本时发射


    def __init__(self):
        super().__init__()
        self.text = None
        self.initUI()
        self.init_signal_slot()
        self.init_logger()
    def init_logger(self):
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        logging.config.fileConfig("logging.conf")

        # 获取配置好的日志记录器
        self.logger = logging.getLogger("myLogger")
        self.logger.debug('debug')
        self.logger.info('info')
        self.logger.warning('warn')
        self.logger.error('error')
        self.logger.critical('critical')


    def initLLM(self,net,url,api_key,model):
        prompt = ChatPromptTemplate.from_template(FILE_DIALOG_TEMPLATE)
        llm = None

        if net == '内网':
            if len(url)>0 and "http" in url:
                llm = getChainLLM(use_stream=True, openai_base_url=url)
                self.stuff_chain = create_stuff_documents_chain(llm, prompt)
        else:
            if len(api_key)>0 and len(model)>0:
                llm = getLLM(use_stream=True, api_key=api_key,model_name=model)

                self.stuff_chain = create_stuff_documents_chain(llm, prompt)

    def initUI(self):
        self.setWindowTitle('文件对话窗口')
        # 创建布局
        layout = QVBoxLayout()
        self.menu_bar = QMenuBar(self)

        self.menu = QMenu(self.menu_bar)
        self.menu_bar.addMenu(self.menu)
        self.menu.setTitle("功能列表")

        self.save_file = QAction(QIcon(), "保存文件", self.menu_bar)
        self.save_file.triggered.connect(self.file_saved_func)
        self.menu.addAction(self.save_file)

        self.open_file = QAction(QIcon(), "打开分析文件", self.menu_bar)
        self.open_file.triggered.connect(self.open_file_func)
        self.open_file.setObjectName("打开分析文件")
        self.open_file.setStatusTip("打开分析文件")
        self.menu_bar.addAction(self.open_file)

        self.about = QAction(QIcon(''), "&关于", self.menu_bar)
        self.about.setObjectName("关于")
        self.about.setStatusTip("关于")
        self.menu_bar.addAction(self.about)


        layout.setMenuBar(self.menu_bar)

        # 创建目录或文件选择按钮和路径显示的布局
        choice_layout = QHBoxLayout()
        self.path_entry = QLineEdit()
        self.path_button = QPushButton('选择...')
        self.path_button.clicked.connect(self.choose_path)

        # 将选择按钮和路径显示的输入框添加到布局
        choice_layout.addWidget(self.path_entry)
        choice_layout.addWidget(self.path_button)

        # 将选择布局添加到主布局
        layout.addLayout(choice_layout)

        self.setLayout(layout)


        # // 设置字体大小
        self.font = QFont()
        self.font.setPixelSize(14) #12号字体大小，你可以根据需要设置

        # 输出显示
        self.browser_view = QTextBrowser(self)
        self.browser_view.setFont(self.font)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.browser_view)

        layout.addLayout(output_layout)

        # 创建输入框和发送按钮的布局
        send_layout = QHBoxLayout()

        # 对话输入
        self.dialog_label = QLabel('对话输入:')
        self.dialog_entry = QLineEdit()
        self.dialog_entry.setFont(self.font)
        self.dialog_entry.returnPressed.connect(self.send_dialog)
        self.dialog_entry.setFixedHeight(40)

        # 发送按钮
        self.send_button = QPushButton('发送')
        self.send_button.clicked.connect(self.send_dialog)
        send_layout.addWidget(self.dialog_entry)
        send_layout.addWidget(self.send_button)

        layout.addLayout(send_layout)
        self.setLayout(layout)

        self.historys = []
        self.text = ""
        self.docs = []
        self.markdown_text = ""
        self.resp_list = []
        self.response_list = []
        self.question_list = []
        self.response = None
        self.file_flag = False


    def init_signal_slot(self):
        self.update_text_signal.connect(self.browser_view.setMarkdown)  # 连接信号到槽
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)  # 定时器超时连接更新文本的槽
        self.timer.start(10)  # 定时器开始，每1000毫秒触发一次

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_document)  # 定时器超时连接更新文本的槽
        self.check_timer.start(10)  # 定时器开始，每1000毫

    @Slot(str)
    def update_text(self):
        if len(self.response_list) > 0 and self.response is None:
            self.response = self.response_list.pop(0)

        if self.response is not None:
            try:
                chunk = next(self.response)
                self.resp_list.append(chunk)
                self.markdown_text += "".join(self.resp_list)
                self.resp_list.clear()
                self.update_text_signal.emit(self.markdown_text)

                # 滚动到最下面
                cursor = self.browser_view.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.browser_view.setTextCursor(cursor)
            except StopIteration:
                # print("没有更多的信息了")
                self.resp_list.clear()
                self.response = None

    @Slot(str)
    def check_document(self):

        if len(self.response_list) == 0 and self.response is None:
            if len(self.question_list) > 0:
                line = self.question_list.pop(0)
                if len(line) > 0:
                    self.dialog_entry.setText(line.strip())
                    self.send_dialog()



    def choose_path(self):
        try:
            # 弹出选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Supported Files (*.docx *.doc *.xlsx *.xls *.pdf *.txt)")
            self.logger.info("选择要分析文件：",file_path)
            if file_path is not None and len(file_path) > 0:
                self.file_flag = True
                self.path_entry.setText(file_path)  # 将选择的文件路径显示在输入框中
                # self.text = parse_file(file_path)
                self.docs = parse_file_documents(file_path)
                self.logger.info(f"读取文件docs信息，数据量:{len(self.docs)}")
                self.browser_view.setMarkdown(self.markdown_text + "---")
                self.browser_view.append("\n")
                self.markdown_text = self.browser_view.toHtml()

                self.logger.info(f"开始分析docs信息……")

                # 对每个块进行模型推理处理
                for doc in self.docs:
                    self.logger.info("stuff_chain 开始模型对话")

                    resp = self.stuff_chain.stream({"question": "对文档进行总结", "context": [doc], "history": ""})
                    self.logger.info("stuff_chain 完成模型对话")

                    self.response_list.append(resp)

                self.logger.info(f"结束docs信息分析")

        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            self.logger.error(f"错误{str(e)}")
            self.logger.error(traceback.print_exc())
            # 如果需要更详细的堆栈跟踪信息，可以使用以下代码



    def send_dialog(self):
        self.response = None
        self.resp_list.clear()
        self.file_flag = False
        dialog_text = self.dialog_entry.text()
        self.logger.info(f"user question is {dialog_text}")
        if len(dialog_text)>0:
            self.dialog_entry.setText("")
            try:
                self.browser_view.append(f"😜：{dialog_text}")
                self.browser_view.append(f"🤖：")
                self.markdown_text = self.browser_view.toHtml()
                self.historys.append(f"question：{dialog_text}")
                # 对每个块进行模型推理处理
                for doc in self.docs:
                    self.response_list.append(
                        self.stuff_chain.stream({"question": dialog_text, "context": [doc], "history": self.historys}))

            except Exception as e:
                # 记录一条信息
                self.logger.error(str(e))
                QMessageBox.critical(self, "错误", str(e))


    def open_file_func(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择要编辑的md文件", "", "文件类型 (*.md)")
        self.logger.info(f"File opened:{self.file_path}")
        # 首先检测文件编码
        with open(self.file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        with open(self.file_path, "r", encoding=encoding) as file:
            for line in file:
                if len(line)>0:
                    self.question_list.append(line)




    def file_saved_func(self):
        # 打开文件保存对话框
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "",
                                                  "Markdown Files (*.md);;All Files (*)",
                                                  options=options)
        if fileName:
            # 保存 QTextBrowser 中的文本到文件
            try:
                with open(fileName, 'w', encoding='utf-8') as f:
                    f.write(self.browser_view.toMarkdown())
            except UnicodeEncodeError as e:
                self.logger.error(f"Error saving file:{e}")

        self.logger.info(f"File saved:{fileName}")