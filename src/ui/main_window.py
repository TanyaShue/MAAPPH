from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter
)

from src.node_graph.graph_widget import TaskNodeGraph
from src.ui.data_display import DataDisplayWidget
from src.ui.menu_widget import MenuWidget
from src.ui.settings_widget import SettingsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAAPPH")
        self.resize(1200, 800)


        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建垂直分割器用于上下分割
        vertical_splitter = QSplitter(Qt.Vertical)
        # self.setup_splitter_appearance(vertical_splitter)

        # 上半部分容器 - 使用水平分割器分成三份
        horizontal_splitter = QSplitter(Qt.Horizontal)
        self.setup_splitter_appearance(horizontal_splitter)

        # 左侧菜单
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        menu_widget = MenuWidget()
        left_layout.addWidget(menu_widget)

        # 中间设置面板
        settings_widget = SettingsWidget()

        # 右侧数据展示
        data_display = DataDisplayWidget()

        data_display.screen_label.roi_selected.connect(settings_widget.update_roi_from_selection)
        data_display.screen_label.target_selected.connect(settings_widget.update_target_from_selection)

        # 将三个部分添加到水平分割器
        horizontal_splitter.addWidget(left_widget)
        horizontal_splitter.addWidget(settings_widget)
        horizontal_splitter.addWidget(data_display)

        # 设置比例为40:20:40
        horizontal_splitter.setStretchFactor(0, 4)
        horizontal_splitter.setStretchFactor(1, 2)
        horizontal_splitter.setStretchFactor(2, 4)

        # 设置初始大小
        total_width = 1200
        horizontal_splitter.setSizes([
            int(total_width * 0.4),
            int(total_width * 0.2),
            int(total_width * 0.4)
        ])

        # 下半部分节点图
        node_graph = TaskNodeGraph()

        # 将上下部分添加到垂直分割器
        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(node_graph)
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 1)

        # 将垂直分割器添加到主布局
        main_layout.addWidget(vertical_splitter)

        self.setCentralWidget(central_widget)

    def setup_splitter_appearance(self, splitter):
        """设置分割器的外观"""
        # 设置分割条的宽度
        splitter.setHandleWidth(3)

        # 设置分割条的样式，垂直方向透明渐变
        stylesheet = """
            QSplitter::handle {
                border: 1px solid #333333;
            }
            QSplitter::handle:vertical {
                height: 3px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0),
                    stop: 0.5 rgba(102, 102, 102, 255),
                    stop: 1 rgba(255, 255, 255, 0)
                );
            }
            QSplitter::handle:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0),
                    stop: 0.5 rgba(153, 153, 153, 255),
                    stop: 1 rgba(255, 255, 255, 0)
                );
            }
            QSplitter::handle:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0),
                    stop: 0.5 rgba(187, 187, 187, 255),
                    stop: 1 rgba(255, 255, 255, 0)
                );
            }
        """
        splitter.setStyleSheet(stylesheet)

