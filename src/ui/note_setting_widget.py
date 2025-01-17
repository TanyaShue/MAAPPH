from pathlib import Path
from typing import Optional

from PySide2.QtCore import QPoint, Signal, Qt
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                               QCheckBox, QSpinBox, QLineEdit, QScrollArea,
                               QDoubleSpinBox, QFrame, QPushButton)

from src.utils.maa_controller import MaaController
from src.utils.task_node import TaskNode, TaskNodeManager


class NoteSettingWidget(QWidget):
    save_settings_signal = Signal(TaskNode)
    def __init__(self, settings: Optional[TaskNode] = None):
        super().__init__()
        self.task_node_manager = TaskNodeManager()
        self.node_file_name = None
        self.node = None
        self.main_layout = None
        self.settings_title = None
        self.sections = {}  # Store section layouts for easy access
        self.input_fields = {}  # Store input fields for each section
        self.settings = settings or TaskNode()
        self.init_ui()
        self.setup_bindings()
        self.update_ui_from_settings(self.settings)
        self.maa_controller = MaaController()
        self.settings.signals.property_changed.connect(self.update_settings_when_property_changed)

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

    def update_settings_when_property_changed(self, field: str, value: object):
        self.update_ui_from_settings(self.settings)

    def save_node(self):
        self.save_settings_signal.emit(self.settings)

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
        # layout.addLayout(self.create_row("template:", self.template_edit))
        layout.addLayout(self.create_section("template", "图片名称"))

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

        # Create sections with their labels
        sections_config = {
            "next": "下一个任务:",
            "interrupt": "中断任务:",
            "on_error": "错误处理任务:"
        }

        for section_name, label_text in sections_config.items():
            layout.addLayout(self.create_section(section_name, label_text))

        return group

    def create_section(self, section_name, label_text):
        section_layout = QHBoxLayout()
        self.sections[section_name] = section_layout
        self.input_fields[section_name] = []

        # Left label
        label = QLabel(label_text)
        label.setFixedWidth(150)
        section_layout.addWidget(label)

        # Right container
        right_container = QVBoxLayout()

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # Store scroll_layout for later access
        self.sections[f"{section_name}_scroll"] = scroll_layout

        # Add a horizontal layout to contain scroll area and button
        scroll_and_button_layout = QHBoxLayout()

        # Add scroll area to the left
        scroll_and_button_layout.addWidget(scroll_area)

        # Add button to the right
        add_button = QPushButton("添加")
        add_button.setFixedWidth(60)
        add_button.clicked.connect(lambda: self.add_row(section_name))
        scroll_and_button_layout.addWidget(add_button, alignment=Qt.AlignRight)

        # Add scroll_and_button_layout to the right container
        right_container.addLayout(scroll_and_button_layout)

        # Add right_container to the section layout
        section_layout.addLayout(right_container)
        return section_layout

    def update_section(self, section_name: str, values: list[str] | str):
        """Create or update a section with the given values."""
        if section_name not in self.sections:
            return

        # 如果 values 是字符串，将其转换为单元素列表
        if isinstance(values, str):
            values = [values]

        # Clear existing rows
        self.clear_section(section_name)

        # Add new rows
        for value in values:
            self.add_row(section_name, value)

    def get_section_values(self, section_name: str) -> list[str]:
        """Get all non-empty values from a section"""
        if section_name not in self.input_fields:
            return []

        return [field.text().strip()
                for field in self.input_fields[section_name]
                if field.text().strip()]

    def add_row(self, section_name: str, initial_value: str = ""):
        scroll_layout = self.sections.get(f"{section_name}_scroll")
        if not scroll_layout:
            return

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        input_field = QLineEdit()
        input_field.setPlaceholderText("输入任务名称")
        input_field.setText(initial_value)

        # Connect the textChanged signal to the dynamic callback
        callback_name = f"on_{section_name}_section_changed"
        if hasattr(self, callback_name):
            input_field.textChanged.connect(lambda: getattr(self, callback_name)())

        delete_button = QPushButton("删除")
        delete_button.setFixedWidth(50)
        delete_button.clicked.connect(
            lambda: self.remove_row(section_name, row_widget, input_field))

        row_layout.addWidget(input_field)
        row_layout.addWidget(delete_button)
        scroll_layout.addWidget(row_widget)

        self.input_fields[section_name].append(input_field)

    def remove_row(self, section_name: str, row_widget: QWidget, input_field: QLineEdit):
        scroll_layout = self.sections.get(f"{section_name}_scroll")
        if scroll_layout:
            scroll_layout.removeWidget(row_widget)
            self.input_fields[section_name].remove(input_field)
            row_widget.deleteLater()

            # Trigger the change callback
            callback_name = f"on_{section_name}_section_changed"
            if hasattr(self, callback_name):
                getattr(self, callback_name)()

    def clear_section(self, section_name: str):
        """Clear all rows in a section"""
        if section_name not in self.input_fields:
            return

        scroll_layout = self.sections.get(f"{section_name}_scroll")
        if not scroll_layout:
            return

        for input_field in self.input_fields[section_name]:
            row_widget = input_field.parentWidget()
            scroll_layout.removeWidget(row_widget)
            row_widget.deleteLater()

        self.input_fields[section_name].clear()

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

    def load_settings_from_node(self):
        """Load settings from a MyNode instance's note_data attribute."""
        try:
            self.node_file_name = self.task_node_manager.get_current_file_path()
            self.node = self.task_node_manager.selected_node
            # 创建新设置对象
            self.settings = type(self.node)()

            # 使用copy_from方法复制属性
            self.settings.copy_from(self.node)
            self.settings.signals.property_changed.connect(self.update_settings_when_property_changed)

            # 更新UI
            self.update_ui_from_settings(self.settings)

        except Exception as e:
            print(f"Error loading settings from node: {e}")
            raise  # 抛出异常以便更好地调试

    def setup_bindings(self):
        """简单直接的双向绑定设置"""
        # UI控件到settings的绑定
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
        self.roi_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'roi', text))
        self.roi_offset_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'roi_offset', text))
        self.threshold_spin.valueChanged.connect(
            lambda value: setattr(self.settings, 'threshold', value))
        self.expected_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'expected', text))
        self.template_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'template', text))
        self.target_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'target', text))
        self.target_offset_edit.textChanged.connect(
            lambda text: setattr(self.settings, 'target_offset', text))
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

    def update_ui_from_settings(self, settings: TaskNode):
        """从settings更新UI控件的值"""
        self.settings = settings
        if not settings:
            return
        # 从settings更新到UI控件
        self.settings_title.setText(settings.NODE_NAME or '')
        self.recognition_combo.setCurrentText(settings.recognition or 'DirectHit')
        self.actions_combo.setCurrentText(settings.action or 'DoNothing')
        self.enabled_check.setChecked(bool(settings.enabled) or True)
        self.focus_check.setChecked(bool(settings.focus))
        self.inverse_check.setChecked(bool(settings.inverse))
        self.roi_edit.setText(str(settings.roi or ''))
        self.roi_offset_edit.setText(str(settings.roi_offset or ''))
        self.threshold_spin.setValue(settings.threshold or 0.7)
        self.expected_edit.setText(settings.expected or '')
        self.target_edit.setText(str(settings.target or ''))
        self.target_offset_edit.setText(str(settings.target_offset or ''))
        self.rate_limit_spin.setValue(settings.rate_limit or 1000)
        self.timeout_spin.setValue(settings.timeout or 20000)
        self.pre_delay_spin.setValue(settings.pre_delay or 200)
        self.post_delay_spin.setValue(settings.post_delay or 200)
        self.pre_freeze_spin.setValue(settings.pre_wait_freezes or 0)
        self.post_freeze_spin.setValue(settings.post_wait_freezes or 0)

        # 更新sections
        if hasattr(settings, 'next'):
            self.update_section('next', settings.next or ["",""])
        if hasattr(settings, 'interrupt'):
            self.update_section('interrupt', settings.interrupt or ["",""])
        if hasattr(settings, 'on_error'):
            self.update_section('on_error', settings.on_error or ["",""])
        if hasattr(settings, 'template'):
            self.update_section('template', settings.template or ["",""])

    # Section相关的方法
    def on_next_section_changed(self):
        """当next section变化时更新settings"""
        values = self.get_section_values('next')
        setattr(self.settings, 'next', values)

    def on_interrupt_section_changed(self):
        """当interrupt section变化时更新settings"""
        values = self.get_section_values('interrupt')
        setattr(self.settings, 'interrupt', values)

    def on_error_section_changed(self):
        """当error section变化时更新settings"""
        values = self.get_section_values('on_error')
        setattr(self.settings, 'on_error', values)

    def on_template_section_changed(self):
        """当template section变化时更新settings"""
        values = self.get_section_values('template')
        setattr(self.settings, 'template', values)

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

            # 更新settings对象
            self.settings.action="Click"
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
                self.settings.recognition = "OCR"
            except Exception :
                self.expected_edit.setText("")

                self.expected_edit.setPlaceholderText("识别失败")

    def update_template_path(self, path: str):
        """
        更新 template 路径，确保 template 始终是 list[str] 类型。
        """
        self.settings.recognition = "FeatureMatch"

        # 确保 template 是 list[str]
        if isinstance(self.settings.template, str):
            self.settings.template = [self.settings.template]
        elif self.settings.template is None:
            self.settings.template = []

        # 添加新的路径到 template 列表
        self.settings.template.append(path)
        # 更新 UI
        self.update_ui_from_settings(self.settings)

    def save_settings_and_next(self):
        """保存设置并跳转到下一个节点"""
        self.save_settings_and_add("next")

    def save_settings_and_interrupt(self):
        """保存设置并添加中断节点"""
        self.save_settings_and_add("interrupt")

    def save_settings_and_on_error(self):
        """保存设置并添加错误处理节点"""
        self.save_settings_and_add("on_error")

    def save_settings_and_add(self, attribute: str):
        """
        保存设置并将新节点名称添加到指定属性。

        :param attribute: 要更新的 settings 属性名称 (如 'next', 'interrupt', 'on_error')。
        """
        new_setting = TaskNode()
        new_node_name = self.generate_unique_node_name()
        new_setting.NODE_NAME = new_node_name

        attr_list = getattr(self.settings, attribute, None)
        if attr_list is None:
            setattr(self.settings, attribute, [new_node_name])
        else:
            attr_list.append(new_node_name)
        # print(attr_list)

        self.save_node()
        self.settings = new_setting
        self.update_ui_from_settings(self.settings)

    def generate_unique_node_name(self) -> str:
        """
        生成唯一的节点名称。

        :return: 唯一的节点名称。
        """
        # 提取文件名并去掉 .json 后缀
        base_name = Path(self.node_file_name).stem

        step = 1
        while True:
            new_node_name = f"{base_name}_step_{step}"

            # 假设 get_node_by_name 是方法，检查节点名称是否已存在
            if self.task_node_manager.get_node_by_name(new_node_name) is None:
                return new_node_name

            step += 1
