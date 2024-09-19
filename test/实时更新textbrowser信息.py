import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QLineEdit, QTextEdit
from PySide6.QtCore import QTimer, Signal, Slot


class MainWindow(QMainWindow):
    update_text_signal = Signal(str)  # 定义一个信号，当需要更新文本时发射

    def __init__(self):
        super().__init__()
        self.text_browser = QTextBrowser()
        self.line_text = QTextEdit()

        self.init_ui()
        self.init_signal_slot()
        self.text = ""

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        layout.addWidget(self.line_text)
        central_widget.setLayout(layout)

    def init_signal_slot(self):
        self.update_text_signal.connect(self.text_browser.setMarkdown)  # 连接信号到槽
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)  # 定时器超时连接更新文本的槽
        self.timer.start(1000)  # 定时器开始，每1000毫秒触发一次


    @Slot(str)
    def update_text(self):
        text = self.line_text.toPlainText()
        self.update_text_signal.emit(text)  # 发射信号


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


