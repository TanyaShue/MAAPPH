import json
import os

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QSizePolicy
from Qt import QtWidgets
from Qt.QtCore import QPropertyAnimation, QEasingCurve
from Qt.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox
)

from NodeGraphQt import NodeGraph, BaseNode, NodeBaseWidget
from src.utils.app_config import Config
from src.utils.task_node import TaskNode


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
        # self.content_widget.setMaximumHeight(200)  # Default content height
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

        self.content_height_animation.valueChanged.connect(self.update_parent_size)
        self.panel_height_animation.valueChanged.connect(self.update_parent_size)
        self.content_height_animation.start()
        self.panel_height_animation.start()
        self.is_expanded = not self.is_expanded

    def update_parent_size(self):
        """Notify the parent window to adjust size."""
        if self.parent():
            self.parent().adjustSize()


class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 设置背景
        palette = self.palette()
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 使用垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 简略信息面板（默认展开）
        self.brief_panel = SmoothCollapsiblePanel("Brief Information")
        self.brief_content = QWidget()
        self.brief_layout = QVBoxLayout(self.brief_content)

        # 创建图片标签
        self.image_label = QLabel()
        self.image_label.setMinimumSize(200, 150)  # 设置最小尺寸
        self.image_label.setScaledContents(True)  # 允许图片缩放
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background-color: #f5f5f5;")

        self.brief_layout.addWidget(self.image_label)
        self.brief_panel.add_content(self.brief_content)
        layout.addWidget(self.brief_panel)

        # 详细信息面板（默认折叠）
        self.detail_panel = SmoothCollapsiblePanel("Detailed Information")
        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)

        # 添加详细信息的内容（可以根据需要添加更多控件）
        detail_label = QLabel("这里是详细信息的内容")
        self.detail_layout.addWidget(detail_label)

        self.detail_panel.add_content(self.detail_content)
        layout.addWidget(self.detail_panel)

        # 默认状态：展开简略信息，折叠详细信息
        self.detail_panel.toggle_content()  # 折叠详细信息

        # 添加弹性空间
        layout.addStretch()

        # 设置默认的简略信息
        self.set_brief_info()

    def set_brief_info(self, image_path=None):
        """设置简略信息（图片）"""
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
                return

        # 如果没有图片路径或图片加载失败，显示默认文本
        self.image_label.clear()
        self.image_label.setText("暂无简略信息")
        self.image_label.setAlignment(Qt.AlignCenter)


class DynamicNodeWidgetWrapper(NodeBaseWidget):
    """
    Wrapper for a node with a dynamic number of input fields.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the name for the node property
        self.set_name("dynamic_widget")

        # Set the label above the widget
        # self.set_label("Dynamic Input Fields")

        # Set the custom widget
        self.set_custom_widget(CustomWidget())

        # Connect signals and slots
        self.wire_signals()

    def wire_signals(self):
        # widget = self.get_custom_widget()
        pass
    def on_btn_add_clicked(self):
        """
        Handles adding a new input field dynamically.
        """

        pass
        # No need to reconnect signals; they are handled within the widget

    def get_value(self):
        """
        Get the values of all input fields as a concatenated string.
        # """

        pass

    def set_value(self, value):
        """
        Set values to the input fields.
        """

        pass


class MyNode(BaseNode):
    """
    Example node with automatic connection capabilities based on node data.
    """

    __identifier__ = 'io.github.jchanvfx'
    NODE_NAME = 'my node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.images_path = None
        self.add_input('in', multi_input=True)
        self.add_output('next')
        self.add_output('interrupt')
        self.add_output('error')
        self.note_data = None
        node_widget = DynamicNodeWidgetWrapper(self.view)
        self.add_custom_widget(node_widget, tab='Custom')
        # self._check_and_create_connections()

    def on_input_connected(self, in_port, out_port):
        # print("hello world")
        # in_port.connect_to(out_port)
        self.update()

    def update(self):
        super().update()
        # Original config loading logic
        current_dir = os.getcwd()
        config_path = os.path.join(current_dir, "config", "app_config.json")
        app_config = Config.from_file(config_path)
        self.images_path = app_config.maa_resource_path

        # New connection logic
        self._check_and_create_connections()

        # Original widget update logic
        custom_widgets = self.view.widgets
        if not custom_widgets:
            return

        wrapper_widget = next(iter(custom_widgets.values()), None)
        if not wrapper_widget:
            return

        custom_widget = wrapper_widget.get_custom_widget()
        if not custom_widget:
            return

        if self.note_data and 'template' in self.note_data:
            template = self.note_data['template']
            if isinstance(template, str):
                image_path = os.path.join(self.images_path, "image", template)
                custom_widget.set_brief_info(image_path)
            elif isinstance(template, list):
                custom_widget.set_brief_info(template[0])
        else:
            custom_widget.set_brief_info(None)

    def _check_and_create_connections(self):
        """
        Check all nodes in the graph for references to this node and create connections.
        """
        if not self.graph:
            return

        current_node_name = self.NODE_NAME

        # Check each node in the graph
        for node in self.graph.all_nodes():
            if node == self or not node.note_data:  # Skip self and nodes without note_data
                continue

            # Define fields to check
            fields = ['next', 'interrupt', 'error']

            for field in fields:
                if field in node.note_data:
                    target_list = node.note_data[field]
                    if isinstance(target_list, str):
                        target_list = [target_list]

                    if current_node_name in target_list:
                        output_port = node.get_output(field)
                        if output_port:
                            output_port.connect_to(self.get_input('in'))
                            # self._connect_ports(self.get_input('in'), output_port)

class TaskNodeGraph(QtWidgets.QWidget):
    note_select =Signal(MyNode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.node_from_path = None
        self.task_data = {}  # Initialize task_data here
        layout = QtWidgets.QVBoxLayout(self)
        self.node_graph = NodeGraph()
        from pathlib import Path
        BASE_PATH = Path(__file__).parent.resolve()

        hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
        self.node_graph.set_context_menu_from_file(hotkey_path, 'graph')
        self.node_graph.register_node(MyNode)
        self.node_graph.set_acyclic(False)
        self.node_graph.set_pipe_style(2)
        self.node_graph.set_grid_mode(False)
        self.node_graph.node_double_clicked.connect(self.on_node_double_clicked)
        self.nodes = {}
        # self.create_nodes()

        viewer = self.node_graph.viewer()
        layout.addWidget(viewer)
    def on_node_double_clicked(self,node):
        # print(node.name)
        self.note_select.emit(node)


    def create_nodes_from_json(self,json_file_path):
        self.nodes={} # 清空节点
        y_pos = 0
        x_pos =0
        self.node_from_path = f"{json_file_path}_bak"
        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                task_data = json.load(file)
        except FileNotFoundError:
            print(FileNotFoundError)
        self.task_data = task_data
        self.node_graph.clear_session()
        # 创建节点
        for task_name, task_config in self.task_data.items():
            node = self.node_graph.create_node('io.github.jchanvfx.MyNode', name=task_name, pos=[x_pos, y_pos])
            node.note_data = task_config
            # print(task_config)
            x_pos += 1000
            # y_pos += 100
            self.nodes[task_name] = node
            node.update()
        nodes = self.node_graph.selected_nodes() or self.node_graph.all_nodes()
        self.node_graph.auto_layout_nodes(nodes=nodes, down_stream=False)

    def add_node(self, node: TaskNode):
        # Create a dictionary to store the node configuration
        node_config = {}

        # Get all fields from the dataclass
        for field in node.__dataclass_fields__:
            if (field != 'NODE_NAME' and
                    field != 'signals'):
                # Get value from the private field
                value = getattr(node, f"_{field}")
                if value is not None:  # Only include non-None values
                    node_config[field] = value

        # Add the node configuration to task_data
        self.task_data[node.NODE_NAME] = node_config
        if node.NODE_NAME in self.nodes:
            # Update existing node
            existing_node = self.nodes[node.NODE_NAME]
            existing_node.note_data = node_config
        else:
        # Create a new node in the graph
            x_pos = len(self.nodes) * 1000  # Maintain the same spacing as in create_nodes_from_json
            y_pos = 0
            new_node = self.node_graph.create_node('io.github.jchanvfx.MyNode',
                                                   name=node.NODE_NAME)
            new_node.note_data = node_config

            # Add to nodes dictionary
            self.nodes[node.NODE_NAME] = new_node
        self.save_nodes_to_json()

    def save_nodes_to_json(self):
        try:
            if self.node_from_path is None:
                self.node_from_path = "nodes.json"
            # 将节点数据保存到字典
            nodes_data = {}
            for node_name, node in self.nodes.items():
                nodes_data[node_name] = node.note_data

            # 将字典写入到 JSON 文件
            with open(self.node_from_path, "w", encoding="utf-8") as file:
                json.dump(nodes_data, file, ensure_ascii=False, indent=4)

            print(f"Nodes successfully saved to {self.node_from_path}")
        except Exception as e:
            print(f"An error occurred while saving nodes to JSON: {e}")
