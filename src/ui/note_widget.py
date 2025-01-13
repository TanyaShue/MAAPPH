from dataclasses import dataclass
from typing import List, Optional, Union

from PySide2.QtCore import QPoint
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                               QCheckBox, QSpinBox, QLineEdit, QTextEdit, QScrollArea,
                               QDoubleSpinBox, QFrame, QPushButton)

from src.node_graph.graph_widget import MyNode
from src.utils.maa_controller import MaaController


@dataclass
class TaskNode:
    NODE_NAME: Optional[str] = None
    recognition: Optional[str] = None
    action: Optional[str] = None
    enabled: Optional[bool] = None
    focus: Optional[bool] = None
    inverse: Optional[bool] = None
    roi: Optional[List[int]] = None
    roi_offset: Optional[List[int]] = None
    threshold: Optional[float] = None
    expected: Optional[str] = None
    target: Optional[Union[str, List[int]]] = None
    template: Optional[Union[str, List[str]]] = None
    target_offset: Optional[List[int]] = None
    next: Optional[List[str]] = None
    interrupt: Optional[List[str]] = None
    on_error: Optional[List[str]] = None
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    pre_delay: Optional[int] = None
    post_delay: Optional[int] = None
    pre_wait_freezes: Optional[int] = None
    post_wait_freezes: Optional[int] = None

class NoteWidget(QWidget):

    def __init__(self, settings: Optional[TaskNode] = None):
        super().__init__()
        self.node = None
        self.main_layout = None
        self.settings_title = None
        self.settings = settings or TaskNode()
        self.init_ui()
        self.load_settings()
        self.setup_bindings()
        self.maa_controller = MaaController()

    def init_ui(self):
        # 创建主布局
        # self.main_layout = QVBoxLayout(self)
        setting_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        # 标题
        self.settings_title = QLineEdit(self.settings.NODE_NAME)
        # self.settings_title.setStyleSheet("font-size: 14pt; font-weight: bold;")

        layout.addLayout(self.create_row("节点详情:", self.settings_title))
        # layout.addWidget(self.settings_title)

        # 添加各个配置组
        groups = [
            ("基础配置", self.create_basic_group),
            ("算法配置", self.create_algo_group),
            ("目标配置", self.create_target_group),
            # ("动作配置", self.create_action_group),
            ("任务流配置", self.create_flow_group),
            ("时间配置", self.create_timing_group)
        ]

        for title, create_func in groups:
            group = create_func()
            group.setFrameStyle(QFrame.StyledPanel)
            layout.addWidget(group)
        scroll.setWidget(content_widget)
        setting_layout.addWidget(scroll)

        # 添加保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_node)
        setting_layout.addWidget(save_button)

        self.main_layout=setting_layout

    def save_node(self):
        # self.settings=self.get_settings()
        print(self.settings)

    def create_row(self, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(150)
        row.addWidget(label)
        row.addWidget(widget)
        return row

    def create_target_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("目标配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.target_edit = QLineEdit()
        self.target_offset_edit = QLineEdit()
        self.expected_edit = QLineEdit()
        self.template_edit = QLineEdit()


        self.target_edit.setPlaceholderText("true/任务名/[x,y,w,h]")
        self.target_offset_edit.setPlaceholderText("[x, y, w, h]")
        self.expected_edit.setPlaceholderText("匹配字符")
        self.template_edit.setPlaceholderText("图片名称")

        layout.addLayout(self.create_row("目标位置:", self.target_edit))
        layout.addLayout(self.create_row("目标偏移:", self.target_offset_edit))
        layout.addLayout(self.create_row("expected:", self.expected_edit))
        layout.addLayout(self.create_row("template:", self.template_edit))

        return group

    def create_basic_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("基础配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # 创建并保存控件引用
        self.recognition_combo = QComboBox()
        self.recognition_combo.addItems([
            "DirectHit", "TemplateMatch", "FeatureMatch", "ColorMatch",
            "OCR", "NeuralNetworkClassify", "NeuralNetworkDetect", "Custom"
        ])

        self.actions_combo = QComboBox()
        self.actions_combo.addItems([
            "DoNothing", "Click", "Swipe", "MultiSwipe", "Key",
            "InputText", "StartApp", "StopApp", "StopTask", "Command", "Custom"
        ])

        self.enabled_check = QCheckBox("启用任务")
        self.focus_check = QCheckBox("关注任务")
        self.inverse_check = QCheckBox("反转识别结果")

        layout.addLayout(self.create_row("识别算法类型:", self.recognition_combo))
        layout.addLayout(self.create_row("执行动作:", self.actions_combo))
        layout.addWidget(self.enabled_check)
        layout.addWidget(self.focus_check)
        layout.addWidget(self.inverse_check)

        return group

    def create_algo_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("算法配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.roi_edit = QLineEdit()
        self.roi_offset_edit = QLineEdit()
        self.threshold_spin = QDoubleSpinBox()

        self.roi_edit.setPlaceholderText("[x, y, w, h]")
        self.roi_offset_edit.setPlaceholderText("[x, y, w, h]")
        self.threshold_spin.setRange(0, 1)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setValue(0.7)

        layout.addLayout(self.create_row("识别区域(ROI):", self.roi_edit))
        layout.addLayout(self.create_row("ROI偏移:", self.roi_offset_edit))
        layout.addLayout(self.create_row("匹配阈值:", self.threshold_spin))

        return group

    def create_action_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("动作配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.target_edit = QLineEdit()
        self.target_offset_edit = QLineEdit()

        self.target_edit.setPlaceholderText("true/任务名/[x,y,w,h]")
        self.target_offset_edit.setPlaceholderText("[x, y, w, h]")

        layout.addLayout(self.create_row("目标位置:", self.target_edit))
        layout.addLayout(self.create_row("目标偏移:", self.target_offset_edit))

        return group

    def create_flow_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("任务流配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # Next Task Section
        layout.addLayout(self.create_section("下一个任务:"))
        # Interrupt Task Section
        layout.addLayout(self.create_section("中断任务:"))
        # Error Handling Task Section
        layout.addLayout(self.create_section("错误处理任务:"))

        return group

    def create_section(self, label_text):
        section_layout = QHBoxLayout()

        # Left label
        label = QLabel(label_text)
        label.setFixedWidth(150)
        section_layout.addWidget(label)

        # Right container with scroll area and add button
        right_container = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        right_container.addWidget(scroll_area)

        # Add button below the scroll area
        add_button = QPushButton("添加")
        add_button.setFixedWidth(60)
        add_button.clicked.connect(lambda: self.add_row(scroll_layout))
        right_container.addWidget(add_button)

        # Add initial two rows
        self.add_row(scroll_layout)
        self.add_row(scroll_layout)

        section_layout.addLayout(right_container)

        return section_layout

    def add_row(self, scroll_layout):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        input_field = QLineEdit()
        input_field.setPlaceholderText("输入任务名称")
        delete_button = QPushButton("删除")
        delete_button.setFixedWidth(50)
        delete_button.clicked.connect(lambda: self.remove_row(row_widget, scroll_layout))

        row_layout.addWidget(input_field)
        row_layout.addWidget(delete_button)

        scroll_layout.addWidget(row_widget)

    def remove_row(self, row_widget, scroll_layout):
        # Remove the specified row widget
        scroll_layout.removeWidget(row_widget)
        row_widget.deleteLater()
        row_widget = None

    def create_timing_group(self):
        group = QFrame()
        layout = QVBoxLayout(group)

        title = QLabel("时间配置")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.rate_limit_spin = QSpinBox()
        self.timeout_spin = QSpinBox()
        self.pre_delay_spin = QSpinBox()
        self.post_delay_spin = QSpinBox()
        self.pre_freeze_spin = QSpinBox()
        self.post_freeze_spin = QSpinBox()

        # 配置范围
        self.rate_limit_spin.setRange(0, 10000)
        self.timeout_spin.setRange(0, 60000)
        self.pre_delay_spin.setRange(0, 5000)
        self.post_delay_spin.setRange(0, 5000)
        self.pre_freeze_spin.setRange(0, 5000)
        self.post_freeze_spin.setRange(0, 5000)

        # 设置默认值
        self.rate_limit_spin.setValue(1000)
        self.timeout_spin.setValue(20000)
        self.pre_delay_spin.setValue(200)
        self.post_delay_spin.setValue(200)

        timing_settings = [
            ("识别速率限制(ms):", self.rate_limit_spin),
            ("超时时间(ms):", self.timeout_spin),
            ("执行前延迟(ms):", self.pre_delay_spin),
            ("执行后延迟(ms):", self.post_delay_spin),
            ("执行前等待画面静止(ms):", self.pre_freeze_spin),
            ("执行后等待画面静止(ms):", self.post_freeze_spin)
        ]

        for label, widget in timing_settings:
            layout.addLayout(self.create_row(label, widget))

        return group

    def load_settings(self):
        """从 TaskNode 加载设置到 UI"""
        if self.settings.NODE_NAME is not None:
            self.settings_title.setText(self.settings.NODE_NAME)

        # 基础设置
        if self.settings.recognition is not None:
            self.recognition_combo.setCurrentText(self.settings.recognition)
        if self.settings.action is not None:
            self.actions_combo.setCurrentText(self.settings.action)
        if self.settings.enabled is not None:
            self.enabled_check.setChecked(self.settings.enabled)
        if self.settings.focus is not None:
            self.focus_check.setChecked(self.settings.focus)
        if self.settings.inverse is not None:
            self.inverse_check.setChecked(self.settings.inverse)

        # 算法设置
        if self.settings.roi is not None:
            self.roi_edit.setText(str(self.settings.roi))
        if self.settings.roi_offset is not None:
            self.roi_offset_edit.setText(str(self.settings.roi_offset))
        if self.settings.threshold is not None:
            self.threshold_spin.setValue(self.settings.threshold)

        # 目标设置
        if self.settings.expected is not None:
            self.expected_edit.setText(self.settings.expected)
        if self.settings.target is not None:
            self.target_edit.setText(str(self.settings.target))
        if self.settings.target_offset is not None:
            self.target_offset_edit.setText(str(self.settings.target_offset))

        # 任务流设置
        # if self.settings.next is not None:
        #     self.next_edit.setText(str(self.settings.next))
        # if self.settings.interrupt is not None:
        #     self.interrupt_edit.setText(str(self.settings.interrupt))
        # if self.settings.on_error is not None:
        #     self.on_error_edit.setText(str(self.settings.on_error))

        # 时间设置
        if self.settings.rate_limit is not None:
            self.rate_limit_spin.setValue(self.settings.rate_limit)
        if self.settings.timeout is not None:
            self.timeout_spin.setValue(self.settings.timeout)
        if self.settings.pre_delay is not None:
            self.pre_delay_spin.setValue(self.settings.pre_delay)
        if self.settings.post_delay is not None:
            self.post_delay_spin.setValue(self.settings.post_delay)
        if self.settings.pre_wait_freezes is not None:
            self.pre_freeze_spin.setValue(self.settings.pre_wait_freezes)
        if self.settings.post_wait_freezes is not None:
            self.post_freeze_spin.setValue(self.settings.post_wait_freezes)

    def update_roi_from_selection(self, start_pos: QPoint, end_pos: QPoint):
        """根据选择更新ROI设置"""
        if start_pos and end_pos:
            x = min(start_pos.x(), end_pos.x())
            y = min(start_pos.y(), end_pos.y())
            width = abs(end_pos.x() - start_pos.x())
            height = abs(end_pos.y() - start_pos.y())

            # 更新ROI输入框
            self.settings.roi = [x, y, width, height]

    def update_target_from_selection(self, start_pos: QPoint, end_pos: QPoint):
        """根据选择更新Target设置"""
        if start_pos and end_pos:
            x = min(start_pos.x(), end_pos.x())
            y = min(start_pos.y(), end_pos.y())
            width = abs(end_pos.x() - start_pos.x())
            height = abs(end_pos.y() - start_pos.y())

            # # 更新Target输入框
            # target_text = f"[{x}, {y}, {width}, {height}]"
            # self.target_edit.setText(target_text)

            # 更新settings对象
            self.settings.target = [x, y, width, height]

    def update_expected_from_recognition(self, start_pos: QPoint, end_pos: QPoint):
        """根据识别结果更新Expected设置"""
        if start_pos and end_pos:
            x = min(start_pos.x(), end_pos.x())
            y = min(start_pos.y(), end_pos.y())
            width = abs(end_pos.x() - start_pos.x())
            height = abs(end_pos.y() - start_pos.y())

            # 更新Expected输入框
            try:
                results = self.maa_controller.tasker.post_pipeline("ocr",{
                                                                    "ocr": {"timeout": 1000, "recognition": "OCR",
                                                                            "expected": ".*",
                                                                            "roi": [x, y, width, height]}}).wait().get()

                self.settings.expected = results.nodes[0].recognition.best_result.text
            except Exception :
                self.expected_edit.setText("")

                self.expected_edit.setPlaceholderText("识别失败")

    def update_screenshot_path(self, path):
        self.settings.template = path

    def load_settings_from_node(self, node: MyNode):
        """Load settings from a MyNode instance's note_data attribute."""
        # if not hasattr(node, 'note_data') or not isinstance(node.note_data, dict):
        #     print("Invalid node data. Skipping load.")
        #     return
        if not hasattr(node, 'note_data'):
            node.NODE_NAME ="默认节点"
        if not isinstance(node.note_data, dict):
            node.note_data = {}


        # 1. 清除现有布局
        if self.main_layout:
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.main_layout)

        # 2. 重置设置和标题
        self.settings = TaskNode()
        self.node=node
        self.settings.NODE_NAME = node.NODE_NAME
        note_data = node.note_data
        try:
            # Map note_data to TaskNode attributes
            self.settings.recognition = note_data.get('recognition', self.settings.recognition)
            self.settings.action = note_data.get('action', self.settings.action)
            self.settings.enabled = note_data.get('enabled', self.settings.enabled)
            self.settings.focus = note_data.get('focus', self.settings.focus)
            self.settings.inverse = note_data.get('inverse', self.settings.inverse)

            self.settings.roi = note_data.get('roi', self.settings.roi)
            self.settings.roi_offset = note_data.get('roi_offset', self.settings.roi_offset)
            self.settings.threshold = note_data.get('threshold', self.settings.threshold)

            self.settings.expected = note_data.get('expected', self.settings.expected)
            self.settings.template = note_data.get('template', self.settings.template)
            self.settings.target = note_data.get('target', self.settings.target)
            self.settings.target_offset = note_data.get('target_offset', self.settings.target_offset)

            self.settings.target = note_data.get('custom_action', note_data.get('target', self.settings.target))
            self.settings.target_offset = note_data.get('target_offset', self.settings.target_offset)

            # self.settings.next = note_data.get('next', self.settings.next)
            # self.settings.interrupt = note_data.get('interrupt', self.settings.interrupt)
            # self.settings.on_error = note_data.get('on_error', self.settings.on_error)

            self.settings.rate_limit = note_data.get('rate_limit', self.settings.rate_limit)
            self.settings.timeout = note_data.get('timeout', self.settings.timeout)
            self.settings.pre_delay = note_data.get('pre_delay', self.settings.pre_delay)
            self.settings.post_delay = note_data.get('post_delay', self.settings.post_delay)
            self.settings.pre_wait_freezes = note_data.get('pre_wait_freezes', self.settings.pre_wait_freezes)
            self.settings.post_wait_freezes = note_data.get('post_wait_freezes', self.settings.post_wait_freezes)
        except Exception as e:
            print(f"Error loading settings from node: {e}")
        # Update UI or other components
        # 4. 重新初始化UI并加载设置
        self.init_ui()
        self.setup_bindings()
        self.load_settings()

    def setup_bindings(self):
        """设置 UI 控件与 settings 的双向绑定"""

        # 基础设置绑定
        self.settings_title.textChanged.connect(
            lambda text: setattr(self.settings, 'NODE_NAME', text))

        self.recognition_combo.currentTextChanged.connect(
            lambda text: setattr(self.settings, 'recognition', text))

        self.actions_combo.currentTextChanged.connect(
            lambda text: setattr(self.settings, 'action', text))

        self.enabled_check.stateChanged.connect(
            lambda state: setattr(self.settings, 'enabled', bool(state)))

        self.focus_check.stateChanged.connect(
            lambda state: setattr(self.settings, 'focus', bool(state)))

        self.inverse_check.stateChanged.connect(
            lambda state: setattr(self.settings, 'inverse', bool(state)))

        # 算法设置绑定
        self.roi_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'roi', text))

        self.roi_offset_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'roi_offset', text))

        self.threshold_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'threshold', value))

        # 目标设置绑定
        self.expected_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'expected', text))

        self.target_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'target', text))

        self.target_offset_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'target_offset', text))

        self.template_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'template', text))

        # 任务流设置绑定
        # self.next_edit.textChanged.connect(
        #     lambda text: setattr(self.settings, 'next', text))
        #
        # self.interrupt_edit.textChanged.connect(
        #     lambda text: setattr(self.settings, 'interrupt', text))
        #
        # self.on_error_edit.textChanged.connect(
        #     lambda text: setattr(self.settings, 'on_error', text))

        # 时间设置绑定
        self.rate_limit_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'rate_limit', value))

        self.timeout_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'timeout', value))

        self.pre_delay_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'pre_delay', value))

        self.post_delay_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'post_delay', value))

        self.pre_freeze_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'pre_wait_freezes', value))

        self.post_freeze_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'post_wait_freezes', value))

        # 设置值变化时更新UI的绑定
        def update_ui(name):
            """当settings中的值改变时更新对应的UI控件"""
            value = getattr(self.settings, name, None)
            if value is None:
                return

            if name == 'NODE_NAME':
                self.settings_title.setText(value)
            elif name == 'recognition':
                self.recognition_combo.setCurrentText(value)
            elif name == 'action':
                self.actions_combo.setCurrentText(value)
            elif name == 'enabled':
                self.enabled_check.setChecked(value)
            elif name == 'focus':
                self.focus_check.setChecked(value)
            elif name == 'inverse':
                self.inverse_check.setChecked(value)
            elif name == 'roi':
                self.roi_edit.setText(str(value))
            elif name == 'roi_offset':
                self.roi_offset_edit.setText(str(value))
            elif name == 'threshold':
                self.threshold_spin.setValue(value)
            elif name == 'expected':
                self.expected_edit.setText(value)
            elif name == 'template':
                self.template_edit.setText(value)
            elif name == 'target':
                self.target_edit.setText(str(value))
            elif name == 'target_offset':
                self.target_offset_edit.setText(str(value))
            # elif name == 'next':
            #     self.next_edit.setText(value)
            # elif name == 'interrupt':
            #     self.interrupt_edit.setText(value)
            # elif name == 'on_error':
            #     self.on_error_edit.setText(value)
            elif name == 'rate_limit':
                self.rate_limit_spin.setValue(value)
            elif name == 'timeout':
                self.timeout_spin.setValue(value)
            elif name == 'pre_delay':
                self.pre_delay_spin.setValue(value)
            elif name == 'post_delay':
                self.post_delay_spin.setValue(value)
            elif name == 'pre_wait_freezes':
                self.pre_freeze_spin.setValue(value)
            elif name == 'post_wait_freezes':
                self.post_freeze_spin.setValue(value)

        # 为settings对象添加属性监听
        for attr in dir(self.settings):
            if not attr.startswith('_'):  # 只监听非私有属性
                setattr(self.settings.__class__, attr, property(
                    lambda self, attr=attr: getattr(self, f'_{attr}', None),
                    lambda self, value, attr=attr: (
                        setattr(self, f'_{attr}', value),
                        update_ui(attr)
                    )[0]
                ))