from PySide2.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QSplitter
)
from PySide2.QtCore import Qt

from src.ui.menu_widget import MenuWidget
from src.ui.settings_widget import SettingsWidget
from src.ui.data_display import DataDisplayWidget
from src.node_graph.graph_widget import TaskNodeGraph


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Flow Management")
        self.resize(1200, 800)

        # 创建主中心窗口
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 上半部分水平布局
        top_splitter = QSplitter(Qt.Horizontal)

        # 左侧菜单和设置
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        menu_widget = MenuWidget()
        settings_widget = SettingsWidget()

        left_layout.addWidget(menu_widget)
        left_layout.addWidget(settings_widget)

        # 右侧数据展示
        data_display = DataDisplayWidget()

        top_splitter.addWidget(left_widget)
        top_splitter.addWidget(data_display)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(top_splitter)

        # 下半部分节点图
        node_graph = TaskNodeGraph()
        main_layout.addWidget(node_graph)

        self.setCentralWidget(central_widget)