import json

from NodeGraphQt import NodeGraph, BaseNode,NodeBaseWidget
from Qt import QtWidgets
class MyCustomDynamicWidget(QtWidgets.QWidget):
    """
    Custom widget with dynamic input fields.
    """

    def __init__(self, parent=None):
        super(MyCustomDynamicWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # List to keep track of input fields
        self.input_fields = []

        # Add default input fields
        for i in range(3):
            self.add_input_field()

        # Add button to add new input fields
        self.btn_add = QtWidgets.QPushButton("Add Input Field")
        self.btn_add.clicked.connect(self.add_input_field)

        self.layout.addWidget(self.btn_add)

    def add_input_field(self):
        """
        Add a new input field to the layout.
        """
        input_field = QtWidgets.QLineEdit()
        input_field.setPlaceholderText(f"Input {len(self.input_fields) + 1}")
        self.input_fields.append(input_field)
        self.layout.insertWidget(len(self.input_fields) - 1, input_field)

class DynamicNodeWidgetWrapper(NodeBaseWidget):
    """
    Wrapper for a node with a dynamic number of input fields.
    """

    def __init__(self, parent=None):
        super(DynamicNodeWidgetWrapper, self).__init__(parent)

        # Set the name for the node property
        self.set_name("dynamic_widget")

        # Set the label above the widget
        self.set_label("Dynamic Input Fields")

        # Set the custom widget
        self.set_custom_widget(MyCustomDynamicWidget())

        # Connect signals and slots
        self.wire_signals()

    def wire_signals(self):
        widget = self.get_custom_widget()

        # Connect signals for the dynamically added fields
        for input_field in widget.input_fields:
            input_field.textChanged.connect(self.on_value_changed)

        widget.btn_add.clicked.connect(self.on_btn_add_clicked)

    def on_btn_add_clicked(self):
        """
        Handles adding a new input field dynamically.
        """
        widget = self.get_custom_widget()
        widget.add_input_field()

        # Connect the new input field to the on_value_changed signal
        new_input_field = widget.input_fields[-1]
        new_input_field.textChanged.connect(self.on_value_changed)

        self.update()
    def get_value(self):
        """
        Get the values of all input fields as a concatenated string.
        """
        widget = self.get_custom_widget()
        return "/".join(input_field.text() for input_field in widget.input_fields)

    def set_value(self, value):
        """
        Set values to the input fields.
        """
        widget = self.get_custom_widget()
        values = value.split("/")
        for i, input_field in enumerate(widget.input_fields):
            if i < len(values):
                input_field.setText(values[i])
            else:
                input_field.setText("")

        # If there are more values than fields, add additional fields
        for val in values[len(widget.input_fields):]:
            widget.add_input_field()
            widget.input_fields[-1].setText(val)

        # Connect new input fields to the on_value_changed signal
        for input_field in widget.input_fields[len(values):]:
            input_field.textChanged.connect(self.on_value_changed)


class TaskNode(BaseNode):
    __identifier__ = 'node.task'
    NODE_NAME = 'My Task Node'

    # 定义默认属性
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

    def __init__(self, properties=None):
        super().__init__()
        # 添加输入和输出端口
        self.add_input("", multi_input=True)
        self.add_output("next", multi_output=True)
        self.add_output("interrupt", multi_output=True)
        self.add_output("on_error", multi_output=True)

        # 初始化属性
        self.properties = properties or {}

        # 动态创建控件
        for key, config in self.default_properties.items():
            if key in self.properties:  # 如果传入了属性
                self._add_property_control(key, config)

    def _add_property_control(self, key, config):
        """
        根据属性类型动态添加控件
        """
        property_type = config['type']
        if property_type == 'combo_menu':
            self.add_combo_menu(
                key,
                config['label'],
                config['items'],
                self.properties.get(key, config.get('default', ""))
            )
        elif property_type == 'text_input':
            self.add_text_input(
                key,
                label=config['label'],
                placeholder_text=config.get('placeholder', "")
            )
        elif property_type == 'checkbox':
            self.add_checkbox(
                key,
                config['label'],
                state=self.properties.get(key, config.get('state', False))
            )


class TaskNodeGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.node_graph = NodeGraph()
        self.node_graph.register_node(TaskNode)
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
            node = self.node_graph.create_node('node.task.TaskNode', name=task_name, pos=[x_pos, y_pos])
            x_pos += 100
            y_pos += 500
            self.nodes[task_name] = node

            # 设置节点属性

            for key, value in task_config.items():
                if key in TaskNode.default_properties:
                    node.properties[key] = value
                    node._add_property_control(key, TaskNode.default_properties[key])

        # 连接节点
        for task_name, task_config in self.task_data.items():
            if "next" in task_config:
                next_nodes = task_config["next"]
                if not isinstance(next_nodes, list):
                    next_nodes = [next_nodes]
                for next_node_name in next_nodes:
                    if next_node_name in self.nodes:
                        self.nodes[task_name].outputs()['next'].connect_to(self.nodes[next_node_name].inputs()[""])
