import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton,
                               QVBoxLayout,
                               QStackedWidget, QHBoxLayout, QMessageBox, QComboBox, QLineEdit)

from FileDialog import FileDialogWindow
from ModelDialog import ModelDialogWindow
from MarkdownDialog import MarkdownWindow
from ReadFile import parse_txt
import configparser

from myLogger import logger
from util import openai_base_url


class DialogApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.load_config()

    def initUI(self):
        self.setWindowTitle('主窗口')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('app.ico'))
        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()

        # 创建文件对话窗口和模型对话窗口
        self.file_dialog_window = FileDialogWindow()
        self.model_dialog_window = ModelDialogWindow()
        self.markdown_dialog_window = MarkdownWindow()

        # 将窗口添加到堆叠窗口
        self.stacked_widget.addWidget(self.model_dialog_window)
        self.stacked_widget.addWidget(self.file_dialog_window)
        self.stacked_widget.addWidget(self.markdown_dialog_window)

        # 创建切换按钮
        self.button1 = QPushButton("模型对话", self)
        self.button2 = QPushButton("文件对话", self)
        self.button3 = QPushButton("文件编辑", self)
        self.button4 = QPushButton("关于", self)

        # 连接按钮信号到槽函数
        self.button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.button4.clicked.connect(self.about)


        # 将切换按钮和堆叠窗口添加到主布局
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.button1)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button3)
        buttons_layout.addWidget(self.button4)

        # 创建一个容器部件来放置按钮
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        # 创建一个容器部件来放置设置信息
        set_layout = QHBoxLayout()
        # 创建选择工具的下拉框
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["内网", "外网"])
        self.tool_combo.currentIndexChanged.connect(self.on_tool_changed)
        set_layout.addWidget(self.tool_combo)

        # 创建联动的输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入URL地址")
        self.url_input.textChanged.connect(self.on_tool_changed)

        set_layout.addWidget(self.url_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入通义千问API-KEY")
        self.api_key_input.hide()
        self.api_key_input.textChanged.connect(self.on_tool_changed)

        set_layout.addWidget(self.api_key_input)

        # 创建模型规格选择下拉框
        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen-turbo", "chatglm3-6b", "qwen-plus", "qwen-max"])
        self.model_combo.hide()
        self.model_combo.currentIndexChanged.connect(self.on_tool_changed)

        set_layout.addWidget(self.model_combo)

        # 创建一个容器部件来放置按钮
        set_widget = QWidget()
        set_widget.setLayout(set_layout)


        main_layout.addWidget(buttons_widget)
        main_layout.addWidget(set_widget)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

    def about(self):
        # 创建一个 QMessageBox 实例
        msg_box = QMessageBox()

        # 设置窗口标题
        msg_box.setWindowTitle("关于")
        text = parse_txt("about.md")

        # 设置要显示的文本
        msg_box.setText(text)

        # 设置消息图标类型
        msg_box.setIcon(QMessageBox.Information)

        # 设置标准按钮
        msg_box.setStandardButtons(QMessageBox.Ok)

        # 设置消息框的固定大小
        msg_box.setFixedSize(280, 180)  # 宽度为 300 像素，高度为 200 像素

        # 显示消息框
        msg_box.exec()


    def on_tool_changed(self, index):
        # 根据选择的工具类型，显示或隐藏输入框
        if self.tool_combo.currentText() == "内网":
            self.url_input.show()
            self.api_key_input.hide()
            self.model_combo.hide()
        else:
            self.url_input.hide()
            self.api_key_input.show()
            self.model_combo.show()

        # 保存配置到.ini文件
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'net': self.tool_combo.currentText(),
            'url': self.url_input.text(),
            'api_key': self.api_key_input.text(),
            'model': self.model_combo.currentText()
        }
        with open('config.ini', 'w', encoding="GBK") as configfile:
            config.write(configfile)

        net = self.tool_combo.currentText()
        url = self.url_input.text()
        api_key = self.api_key_input.text()
        model = self.model_combo.currentText()

        self.model_dialog_window.initLLM(net,url,api_key,model)
        self.file_dialog_window.initLLM(net,url,api_key,model)

    def load_config(self):
        logger.info("begin load_config!")
        # 从.ini文件加载配置
        config = configparser.ConfigParser()
        if config.read('config.ini', encoding="GBK"):
            net = config.get('DEFAULT', 'net', fallback='')
            if net == "":
                net = "内网"
            url = config.get('DEFAULT', 'url', fallback='')
            if url == "":
                url = f'{openai_base_url}'
            api_key = config.get('DEFAULT', 'api_key', fallback='')
            model = config.get('DEFAULT', 'model', fallback='')

            self.tool_combo.setCurrentText(net)
            self.url_input.setText(url)
            self.api_key_input.setText(api_key)
            self.model_combo.setCurrentText(model)
            logger.info("begin self.model_dialog_window.initLLM!")
            self.model_dialog_window.initLLM(net,url,api_key,model)
            logger.info("begin self.file_dialog_window.initLLM!")
            self.file_dialog_window.initLLM(net,url,api_key,model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DialogApp()
    ex.showMaximized()
    sys.exit(app.exec())