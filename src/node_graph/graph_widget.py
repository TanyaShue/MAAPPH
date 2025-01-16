import json
import os
from pathlib import Path

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
from src.utils.task_node import TaskNode, TaskNodeManager

# 自定义可折叠面板
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

# 自定义控件
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

# 自定义节点
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
        self.add_input('in', multi_input=True)
        self.add_output('next')
        self.add_output('interrupt')
        self.add_output('on_error')
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
        resource_path = app_config.maa_resource_path

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
                image_path = os.path.join(resource_path, "image", template)
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
            fields = ['next', 'interrupt', 'on_error']

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
    node_select = Signal()  # Changed to more generic name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.node_graph = None
        self.node_manager = TaskNodeManager()  # Add TaskNodeManager
        self.setup_ui()
        self.task_nodes = {}  # Dictionary to store graph nodes: {node_id: graph_node}

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.node_graph = NodeGraph()

        # Setup NodeGraph
        BASE_PATH = Path(__file__).parent.resolve()
        hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
        self.node_graph.set_context_menu_from_file(hotkey_path, 'graph')
        self.node_graph.register_node(MyNode)
        self.node_graph.set_acyclic(False)
        self.node_graph.set_pipe_style(2)
        self.node_graph.set_grid_mode(False)
        self.node_graph.node_double_clicked.connect(self.on_node_double_clicked)

        viewer = self.node_graph.viewer()
        layout.addWidget(viewer)

    def on_node_double_clicked(self, graph_node):
        # Get TaskNode from manager using graph node's id
        self.node_manager.selected_node = self.node_manager.get_node_by_id(graph_node.node_id)
        self.node_select.emit()

    def load_from_file(self, file_path: str):
        """Load nodes from file using TaskNodeManager"""
        if self.node_manager.load_from_file(file_path):
            self.refresh_graph()
            return True
        return False

    def refresh_graph(self):
        """Refresh the entire graph based on TaskNodeManager's nodes"""
        # Clear existing graph
        self.node_graph.clear_session()
        self.task_nodes.clear()

        # Create nodes for each TaskNode in manager
        for task_node in self.node_manager.get_all_nodes():
            self.create_graph_node(task_node)

        # Auto layout all nodes
        nodes = self.node_graph.all_nodes()
        self.node_graph.auto_layout_nodes(nodes=nodes, down_stream=False)

    def create_graph_node(self, task_node: TaskNode) -> MyNode:
        """Create a graph node from a TaskNode"""
        # Convert TaskNode to node configuration
        node_config = task_node.to_dict()
        # node_config.pop('NODE_NAME', None)  # Remove NODE_NAME from config
        # Create graph node
        graph_node = self.node_graph.create_node(
            'io.github.jchanvfx.MyNode',
            name=task_node.NODE_NAME
        )
        graph_node.node_id = task_node.id  # Set the ID to match TaskNode
        graph_node.note_data = node_config

        # Store in nodes dictionary
        self.task_nodes[task_node.id] = graph_node

        graph_node.update()
        return graph_node

    def update_node(self, task_node: TaskNode):
        """Update or create a node in the graph based on a TaskNode"""
        if task_node.id in self.task_nodes:
            # Update existing node
            graph_node = self.task_nodes[task_node.id]
            graph_node.NODE_NAME = task_node.NODE_NAME
            graph_node.note_data = task_node.to_dict()
        else:
            # Create new node
            self.create_graph_node(task_node)
        # Save changes
        self.save_to_file()

    def save_to_file(self, file_path: str = None):
        """Save nodes using TaskNodeManager"""
        # Update positions in TaskNodes before saving
        for node_id, graph_node in self.task_nodes.items():
            task_node = self.node_manager.get_node_by_id(node_id)
            if task_node:
                # You might want to add position storage in TaskNode class
                pos = graph_node.pos()
                # Add position to node_data if needed
                graph_node.note_data['position'] = {'x': pos[0], 'y': pos[1]}

        return self.node_manager.save_to_file(file_path)

    def add_node(self, task_node: TaskNode):
        """Add or update a node in both manager and graph"""
        # Add/update in manager
        self.node_manager.add_node(task_node)

        # Update graph
        self.update_node(task_node)

    def remove_node(self, node_id: str):
        """Remove a node from both manager and graph"""
        # Remove from manager
        self.node_manager.remove_node(node_id)

        # Remove from graph
        if node_id in self.task_nodes:
            graph_node = self.task_nodes[node_id]
            self.node_graph.remove_node(graph_node)
            del self.task_nodes[node_id]

    def get_current_file_path(self):
        """Get current file path from manager"""
        return self.node_manager.get_current_file_path()