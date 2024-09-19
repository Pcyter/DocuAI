import logging

from PySide6.QtWidgets import QTextEdit, \
    QTextBrowser, QVBoxLayout, QMenuBar, QMenu, QHBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QIcon, QAction
import chardet
from logging.config import fileConfig
import logging

class MarkdownWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = ""
        self.initUI()

        self.initLogger()

    def initLogger(self):
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        # 创建一个日志器
        # 将配置文件字符串载入配置
        # logging_config = configparser.ConfigParser()
        logging.config.fileConfig("logging.conf")

        # 获取配置好的日志记录器
        logger = logging.getLogger("Logger")
        logger.debug('debug')
        logger.info('info')
        logger.warning('warn')
        logger.error('error')
        logger.critical('critical')

    def initUI(self):
        self.setWindowTitle('markdown 文件编辑窗口')

        # 创建布局
        layout = QVBoxLayout()

        # 菜单按钮
        self.menu_bar = QMenuBar(self)

        self.menu = QMenu(self.menu_bar)
        self.menu_bar.addMenu(self.menu)
        self.menu.setTitle("功能列表")

        self.open_file = QAction(QIcon(), "打开文件", self.menu_bar)
        self.open_file.triggered.connect(self.open_file_func)
        self.menu.addAction(self.open_file)

        self.save_file = QAction(QIcon(), "保存文件", self.menu_bar)
        self.menu.addAction(self.save_file)
        self.save_file.triggered.connect(self.file_saved_func)

        self.huitui = QAction(QIcon('img/houtui.jpg'), "&回退", self.menu_bar)
        self.huitui.setObjectName("回退")
        self.huitui.setShortcut("Ctrl+q")
        self.huitui.setStatusTip("操作文档回退")

        self.menu_bar.addAction(self.huitui)

        self.qianjin = QAction(QIcon('img/qianjin.jpg'), "&前进", self.menu_bar)
        self.qianjin.setObjectName("qianjin")
        self.qianjin.setShortcut("Ctrl+h")
        self.qianjin.setStatusTip("操作文档前进")

        self.menu_bar.addAction(self.qianjin)

        self.about = QAction(QIcon(''), "&关于", self.menu_bar)
        self.about.setObjectName("关于")
        self.about.setStatusTip("关于")
        self.menu_bar.addAction(self.about)

        layout.setMenuBar(self.menu_bar)


        # self.markdown_layout = QHBoxLayout(self)

        self.content_layout = QHBoxLayout()
        self.markdown_context = QTextEdit(self)
        self.markdown_browser = QTextBrowser(self)
        self.content_layout.addWidget(self.markdown_context)
        self.content_layout.addWidget(self.markdown_browser)

        self.huitui.triggered.connect(self.markdown_context.redo)
        self.qianjin.triggered.connect(self.markdown_context.undo)
        self.markdown_context.textChanged.connect(self.file_changed_func)

        layout.addLayout(self.content_layout)

        self.setLayout(layout)

    def open_file_func(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择要编辑的md文件", "", "文档类型 (*.md *.txt)")
        # 首先检测文件编码
        with open(self.file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']


        with open(self.file_path, "r", encoding=encoding) as f:
            content = f.read()
            self.markdown_context.setText(content)
            self.markdown_browser.setMarkdown(content)

    def file_changed_func(self):
        self.markdown_browser.setMarkdown(self.markdown_context.toPlainText())

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
                    f.write(self.markdown_context.toMarkdown())
            except UnicodeEncodeError as e:
                print("Error saving file:", e)

        print("File saved:", fileName)