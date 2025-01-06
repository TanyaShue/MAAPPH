import json

from Qt import QtWidgets
from Qt.QtCore import QPropertyAnimation, QEasingCurve
from Qt.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QSizePolicy
)

from NodeGraphQt import NodeGraph, BaseNode, NodeBaseWidget


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
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

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


class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 设置背景
        palette = self.palette()
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 使用垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # 添加边距
        layout.setSpacing(10)  # 设置面板间距

        # 第一个面板：识别方法
        panel1 = SmoothCollapsiblePanel("Recognition Settings")
        recognition_layout = QHBoxLayout()
        recognition_label = QLabel("Recognition Method:")
        recognition_combo = QComboBox()
        recognition_combo.addItems([
            "DirectHit", "TemplateMatch", "FeatureMatch",
            "ColorMatch", "OCR", "NeuralNetworkClassify",
            "NeuralNetworkDetect", "Custom"
        ])

        # 调整样式
        recognition_label.setStyleSheet("font-weight: bold;")

        recognition_layout.addWidget(recognition_label)
        recognition_layout.addWidget(recognition_combo)
        recognition_layout.addStretch()  # 添加弹性空间

        panel1_widget = QWidget()
        panel1_widget.setLayout(recognition_layout)
        panel1.add_content(panel1_widget)
        layout.addWidget(panel1)

        # 第二个面板：动作方法
        panel2 = SmoothCollapsiblePanel("Action Settings")
        action_layout = QHBoxLayout()
        action_label = QLabel("Action Method:")
        action_combo = QComboBox()
        action_combo.addItems([
            "DoNothing", "Click", "Swipe", "Key",
            "InputText", "StartApp", "StopApp",
            "StopTask", "Custom"
        ])

        # 调整样式
        action_layout.addWidget(action_label)
        action_layout.addWidget(action_combo)
        action_layout.addStretch()  # 添加弹性空间

        panel2_widget = QWidget()
        panel2_widget.setLayout(action_layout)
        panel2.add_content(panel2_widget)
        layout.addWidget(panel2)

        # 第三个面板：速率限制和超时
        panel3 = SmoothCollapsiblePanel("Rate Limit and Timeout")
        rate_timeout_layout = QVBoxLayout()

        # 速率限制
        rate_limit_label = QLabel("Rate Limit:")
        rate_limit_input = QLineEdit()
        rate_limit_input.setPlaceholderText("1000")

        # 超时
        timeout_label = QLabel("Timeout:")
        timeout_input = QLineEdit()
        timeout_input.setPlaceholderText("1000")

        rate_timeout_layout.addWidget(rate_limit_label)
        rate_timeout_layout.addWidget(rate_limit_input)
        rate_timeout_layout.addSpacing(20)  # 添加间隔
        rate_timeout_layout.addWidget(timeout_label)
        rate_timeout_layout.addWidget(timeout_input)
        rate_timeout_layout.addStretch()  # 添加弹性空间

        panel3_widget = QWidget()
        panel3_widget.setLayout(rate_timeout_layout)
        panel3.add_content(panel3_widget)
        layout.addWidget(panel3)

        # 添加弹性空间，确保布局向上对齐
        layout.addStretch()

        # 设置大小策略为 QSizePolicy.Minimum
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def sizeHint(self):
        # 根据内容动态调整大小
        return self.layout().sizeHint()

    def minimumSizeHint(self):
        # 最小尺寸提示
        return self.layout().minimumSize()

    def apply_settings(self):
        # 收集和处理设置
        print("Settings applied!")

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
    Example node.
    """

    # set a unique node identifier.
    __identifier__ = 'io.github.jchanvfx'

    # set the initial default node name.
    NODE_NAME = 'my node'

    default_properties = {
        'recognition': {
            'type': 'combo_menu',
            'label': 'Recognition',
            'items': [
                "DirectHit", "TemplateMatch", "FeatureMatch",
                "ColorMatch", "OCR", "NeuralNetworkClassify",
                "NeuralNetworkDetect", "Custom"
            ],
            'default': "DirectHit"
        },
        'action': {
            'type': 'combo_menu',
            'label': 'Actions',
            'items': [
                "DoNothing", "Click", "Swipe", "Key",
                "InputText", "StartApp", "StopApp",
                "StopTask", "Custom"
            ],
            'default': "DoNothing"
        },
        'rate_limit': {
            'type': 'text_input',
            'label': "Rate Limit (ms)",
            'placeholder': "1000"
        },
        'timeout': {
            'type': 'text_input',
            'label': "Timeout (ms)",
            'placeholder': "20000"
        },
        'inverse': {
            'type': 'checkbox',
            'label': "Inverse Recognition",
            'state': False
        },
        'enabled': {
            'type': 'checkbox',
            'label': "Enable Task",
            'state': True
        },
        # 更多属性...
    }
    def __init__(self):
        super(MyNode, self).__init__()

        # create input and output port.
        self.add_input('in',multi_input=True)
        self.add_output('next',)
        self.add_output('interrupt')
        self.add_output('error')

        # add custom widget to node with "node.view" as the parent.
        node_widget = DynamicNodeWidgetWrapper(self.view)

        self.add_custom_widget(node_widget, tab='Custom')
    def on_input_connected(self, in_port, out_port):
        self.update()
class TaskNodeGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        debugger = True
        layout = QtWidgets.QVBoxLayout(self)
        self.node_graph = NodeGraph()
        self.node_graph.register_node(MyNode)
        self.node_graph.set_acyclic(False)
        self.node_graph.set_pipe_style(2)
        self.node_graph.set_grid_mode(False)
        json_file_path = "test.json"  # 替换为实际的 JSON 文件路径
        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                task_data = json.load(file)
        except FileNotFoundError:
            print(FileNotFoundError)

        self.task_data = task_data
        self.nodes = {}
        self.create_nodes()

        viewer = self.node_graph.viewer()
        layout.addWidget(viewer)

    def create_nodes(self):
        y_pos = 0
        x_pos =0
        # 创建节点
        for task_name, task_config in self.task_data.items():
            node = self.node_graph.create_node('io.github.jchanvfx.MyNode', name=task_name, pos=[x_pos, y_pos])
            x_pos += 1000
            # y_pos += 100
            self.nodes[task_name] = node

            # 设置节点属性

            # for key, value in task_config.items():
            #     if key in TaskNode.default_properties:
            #         node.properties[key] = value
            #         node._add_property_control(key, TaskNode.default_properties[key])

        # # 连接节点
        # for task_name, task_config in self.task_data.items():
        #     if "next" in task_config:
        #         next_nodes = task_config["next"]
        #         if not isinstance(next_nodes, list):
        #             next_nodes = [next_nodes]
        #         for next_node_name in next_nodes:
        #             if next_node_name in self.nodes:
        #                 self.nodes[task_name].outputs()['next'].connect_to(self.nodes[next_node_name].inputs()[""])
