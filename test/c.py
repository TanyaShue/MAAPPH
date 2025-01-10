import sys

import maa
from Qt.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QGroupBox, QWidget
)
from maa.toolkit import Toolkit


class CollapsiblePanel(QGroupBox):
    def __init__(self, title, content, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        self.setCheckable(True)  # 使标题可以点击
        self.setChecked(True)   # 默认展开
        self.toggled.connect(self.toggle_content)  # 连接信号到槽

        # 添加内容
        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        for widget in content:
            layout.addWidget(widget)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.content_widget)

    def toggle_content(self, checked):
        """根据展开状态显示或隐藏内容"""
        self.content_widget.setVisible(checked)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout(self)

        # 添加面板1
        panel1 = CollapsiblePanel("折叠面板1", [QLabel("内容1"), QLabel("更多内容1")])
        main_layout.addWidget(panel1)

        # 添加面板2
        panel2 = CollapsiblePanel("折叠面板2", [QLabel("内容2"), QLabel("更多内容2")])
        main_layout.addWidget(panel2)

        self.setWindowTitle("QGroupBox 折叠面板")
        self.resize(300, 200)

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec_())
    adb_devices = Toolkit.find_adb_devices()
    print(adb_devices)