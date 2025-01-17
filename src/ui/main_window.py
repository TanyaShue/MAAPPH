import asyncio
import time

from PySide2.QtCore import Qt, QPoint
from PySide2.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter
)

from src.node_graph.graph_widget import TaskNodeGraph
from src.ui.data_display import DataDisplayWidget
from src.ui.note_setting_widget import NoteSettingWidget
from src.ui.setting_widget import SettingWidget
from src.utils.app_config import AdbConfig
from src.utils.maa_controller import MaaController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_config = None
        self.MaaController = MaaController()
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

        # 左侧设置面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        setting_widget = SettingWidget()
        left_layout.addWidget(setting_widget)

        # 中间节点面板
        note_widget = NoteSettingWidget()

        # 右侧数据展示
        data_display = DataDisplayWidget()
        self.data_display = data_display
        # 将三个部分添加到水平分割器
        horizontal_splitter.addWidget(setting_widget)
        horizontal_splitter.addWidget(note_widget)
        horizontal_splitter.addWidget(data_display)

        # 设置比例为40:20:40
        horizontal_splitter.setStretchFactor(0, 2)
        horizontal_splitter.setStretchFactor(1, 2)
        horizontal_splitter.setStretchFactor(2, 4)

        # 下半部分节点图
        node_graph = TaskNodeGraph()

        # 将上下部分添加到垂直分割器
        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(node_graph)
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 2)

        # 将垂直分割器添加到主布局
        main_layout.addWidget(vertical_splitter)

        self.setCentralWidget(central_widget)


        # 连接信号
        data_display.screen_label.roi_selected.connect(note_widget.update_roi_from_selection)
        data_display.screen_label.target_selected.connect(note_widget.update_target_from_selection)
        data_display.screen_label.recognition_from_roi_signal.connect(note_widget.update_expected_from_recognition)
        setting_widget.connect_adb_signal.connect(self.initialize_controller)
        setting_widget.connect_resource_signal.connect(self.initialize_resource)
        setting_widget.open_pipeline_in_node_graph_signal.connect(node_graph.load_from_file)
        node_graph.node_select.connect(note_widget.load_settings_from_node)
        data_display.screen_label.update_screenshot_path.connect(note_widget.update_template_path)
        note_widget.save_settings_signal.connect(node_graph.add_node)
        data_display.screen_label.info_panel.save_and_edit_next_signal.connect(note_widget.save_settings_and_next)
        data_display.screen_label.info_panel.save_and_edit_interrupt_signal.connect(note_widget.save_settings_and_interrupt)
        data_display.screen_label.info_panel.save_and_edit_on_error_signal.connect(note_widget.save_settings_and_on_error)
        data_display.screen_label.clicked_display.connect(self.click_display)

    async def async_initialize_controller(self, adb_config: AdbConfig, user_path: str = "./"):


        successes = await asyncio.to_thread(
            self.MaaController.connect_adb,
            user_path,
            adb_config
        )

        if successes:
            print("MAA初始化成功")
            self.data_display.refresh_screen()

    async def async_initialize_resource(self,resource_path: str):
        successes = await asyncio.to_thread(
            self.MaaController.connect_resource,
            resource_path,
        )

        if successes:
            print("MAA资源初始化成功")

    async def async_clicked_display(self,point:QPoint):
        successes = await asyncio.to_thread(
            self.MaaController.click,
            point.x(),
            point.y(),
        )
        if successes:
            print("点击屏幕成功")
    def initialize_controller(self, adb_config: AdbConfig, user_path: str = "./"):
        asyncio.create_task(self.async_initialize_controller(adb_config, user_path))

    def initialize_resource(self, maa_resource_path: str):
        asyncio.create_task(self.async_initialize_resource(maa_resource_path))
            
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

    def click_display(self,point:QPoint):
        asyncio.create_task(self.async_clicked_display(point))
        self.data_display.refresh_screen()

