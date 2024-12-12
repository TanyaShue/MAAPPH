import sys
from Qt.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                          QLabel, QPushButton, QStackedWidget)
from Qt.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

class SmoothCollapsiblePanel(QWidget):
    def __init__(self, title="Panel", parent=None):
        super().__init__(parent)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Style
        self.setStyleSheet("""
            QWidget { 
                background-color: white; 
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        # Header
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #333;
        """)

        # Toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 15px;
            }
        """)
        self.toggle_button.setText("\u25bc")  # Down arrow
        self.toggle_button.clicked.connect(self.toggle_content)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)

        # Content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        # Main layout
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content_widget)

        # Animations
        self.content_height_animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.content_height_animation.setDuration(300)
        self.content_height_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.panel_height_animation = QPropertyAnimation(self, b"maximumHeight")
        self.panel_height_animation.setDuration(300)
        self.panel_height_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Initial state
        self.is_expanded = True
        self.header_height = self.header.sizeHint().height()
        self.content_widget.setMaximumHeight(200)  # Default content height
        self.setMaximumHeight(self.header_height + 200)

    def add_content(self, widget):
        """Add content to the panel."""
        self.content_layout.addWidget(widget)

    def toggle_content(self):
        """Toggle panel expanded/collapsed state."""
        if self.is_expanded:
            # Collapse animation
            self.content_height_animation.setStartValue(self.content_widget.height())
            self.content_height_animation.setEndValue(0)

            self.panel_height_animation.setStartValue(self.maximumHeight())
            self.panel_height_animation.setEndValue(self.header_height)

            self.toggle_button.setText("\u25b6")  # Right arrow
        else:
            # Expand animation
            self.content_height_animation.setStartValue(0)
            self.content_height_animation.setEndValue(200)  # Adjust to actual content

            self.panel_height_animation.setStartValue(self.maximumHeight())
            self.panel_height_animation.setEndValue(self.header_height + 200)

            self.toggle_button.setText("\u25bc")  # Down arrow

        self.content_height_animation.start()
        self.panel_height_animation.start()
        self.is_expanded = not self.is_expanded


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smooth Collapsible Panels")
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 创建多个面板
        panel1 = SmoothCollapsiblePanel("个人信息")
        panel1.add_content(QLabel("姓名：张三"))
        panel1.add_content(QLabel("邮箱：zhangsan@example.com"))
        layout.addWidget(panel1)

        panel2 = SmoothCollapsiblePanel("工作详情")
        panel2.add_content(QLabel("公司：科技有限公司"))
        panel2.add_content(QLabel("职位：软件工程师"))
        layout.addWidget(panel2)

        layout.addStretch()


def main():
    app = QApplication(sys.argv)
    # 设置全局样式
    app.setStyleSheet("""
        QWidget {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()