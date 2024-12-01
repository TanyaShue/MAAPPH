from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        menu_title = QLabel("功能菜单")
        layout.addWidget(menu_title)

        buttons = [
            "新建任务",
            "导入任务",
            "任务列表",
            "系统设置"
        ]

        for btn_text in buttons:
            btn = QPushButton(btn_text)
            layout.addWidget(btn)

        layout.addStretch()