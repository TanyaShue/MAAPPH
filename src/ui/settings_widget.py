from dataclasses import dataclass
from typing import List, Optional

from PySide2.QtCore import Signal, QPoint
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                               QCheckBox, QSpinBox, QLineEdit, QTextEdit, QScrollArea,
                               QDoubleSpinBox, QFrame)


@dataclass
class BasicSettings:
    recognition_type: str = "DirectHit"
    action_type: str = "StartApp"
    enabled: bool = True
    focused: bool = False
    inverse_recognition: bool = False


@dataclass
class AlgorithmSettings:
    roi: List[int] = None  # [x, y, w, h]
    roi_offset: List[int] = None  # [x, y, w, h]
    threshold: float = 0.7


@dataclass
class ActionSettings:
    target: str = ""  # can be "true", task name, or [x,y,w,h]
    target_offset: List[int] = None  # [x, y, w, h]


@dataclass
class FlowSettings:
    next_tasks: List[str] = None
    interrupt_tasks: List[str] = None
    error_tasks: List[str] = None


@dataclass
class TimingSettings:
    rate_limit_ms: int = 1000
    timeout_ms: int = 20000
    pre_delay_ms: int = 200
    post_delay_ms: int = 200
    pre_freeze_ms: int = 0
    post_freeze_ms: int = 0


class NodeSettings:
    def __init__(self):
        self.basic = BasicSettings()
        self.algorithm = AlgorithmSettings()
        self.action = ActionSettings()
        self.flow = FlowSettings()
        self.timing = TimingSettings()


class SettingsWidget(QWidget):
    roi_selection_requested = Signal()

    def __init__(self, settings: Optional[NodeSettings] = None):
        super().__init__()
        self.settings = settings or NodeSettings()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        # 标题
        settings_title = QLabel("节点详情")
        settings_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(settings_title)

        # 添加各个配置组
        groups = [
            ("基础配置", self.create_basic_group),
            ("算法配置", self.create_algo_group),
            ("动作配置", self.create_action_group),
            ("任务流配置", self.create_flow_group),
            ("时间配置", self.create_timing_group)
        ]

        for title, create_func in groups:
            group = create_func()
            group.setFrameStyle(QFrame.StyledPanel)
            layout.addWidget(group)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_row(self, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(150)
        row.addWidget(label)
        row.addWidget(widget)
        return row

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

        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "DoNothing", "Click", "Swipe", "MultiSwipe", "Key",
            "InputText", "StartApp", "StopApp", "StopTask", "Command", "Custom"
        ])

        self.enabled_check = QCheckBox("启用任务")
        self.focus_check = QCheckBox("关注任务")
        self.inverse_check = QCheckBox("反转识别结果")

        layout.addLayout(self.create_row("识别算法类型:", self.recognition_combo))
        layout.addLayout(self.create_row("执行动作:", self.action_combo))
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

        self.next_edit = QTextEdit()
        self.interrupt_edit = QTextEdit()
        self.on_error_edit = QTextEdit()

        for edit in [self.next_edit, self.interrupt_edit, self.on_error_edit]:
            edit.setMaximumHeight(80)

        self.next_edit.setPlaceholderText("输入任务名称，每行一个")
        self.interrupt_edit.setPlaceholderText("输入中断任务名称，每行一个")
        self.on_error_edit.setPlaceholderText("输入错误处理任务名称，每行一个")

        layout.addLayout(self.create_row("下一个任务:", self.next_edit))
        layout.addLayout(self.create_row("中断任务:", self.interrupt_edit))
        layout.addLayout(self.create_row("错误处理任务:", self.on_error_edit))

        return group

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
        """从 NodeSettings 加载设置到 UI"""
        # 基础设置
        self.recognition_combo.setCurrentText(self.settings.basic.recognition_type)
        self.action_combo.setCurrentText(self.settings.basic.action_type)
        self.enabled_check.setChecked(self.settings.basic.enabled)
        self.focus_check.setChecked(self.settings.basic.focused)
        self.inverse_check.setChecked(self.settings.basic.inverse_recognition)

        # 算法设置
        if self.settings.algorithm.roi:
            self.roi_edit.setText(str(self.settings.algorithm.roi))
        if self.settings.algorithm.roi_offset:
            self.roi_offset_edit.setText(str(self.settings.algorithm.roi_offset))
        self.threshold_spin.setValue(self.settings.algorithm.threshold)

        # 动作设置
        self.target_edit.setText(self.settings.action.target)
        if self.settings.action.target_offset:
            self.target_offset_edit.setText(str(self.settings.action.target_offset))

        # 任务流设置
        if self.settings.flow.next_tasks:
            self.next_edit.setText('\n'.join(self.settings.flow.next_tasks))
        if self.settings.flow.interrupt_tasks:
            self.interrupt_edit.setText('\n'.join(self.settings.flow.interrupt_tasks))
        if self.settings.flow.error_tasks:
            self.on_error_edit.setText('\n'.join(self.settings.flow.error_tasks))

        # 时间设置
        self.rate_limit_spin.setValue(self.settings.timing.rate_limit_ms)
        self.timeout_spin.setValue(self.settings.timing.timeout_ms)
        self.pre_delay_spin.setValue(self.settings.timing.pre_delay_ms)
        self.post_delay_spin.setValue(self.settings.timing.post_delay_ms)
        self.pre_freeze_spin.setValue(self.settings.timing.pre_freeze_ms)
        self.post_freeze_spin.setValue(self.settings.timing.post_freeze_ms)

    def get_settings(self) -> NodeSettings:
        """从 UI 获取设置并返回 NodeSettings 对象"""
        settings = NodeSettings()

        # 基础设置
        settings.basic.recognition_type = self.recognition_combo.currentText()
        settings.basic.action_type = self.action_combo.currentText()
        settings.basic.enabled = self.enabled_check.isChecked()
        settings.basic.focused = self.focus_check.isChecked()
        settings.basic.inverse_recognition = self.inverse_check.isChecked()

        # 算法设置
        roi_text = self.roi_edit.text()
        if roi_text:
            try:
                settings.algorithm.roi = eval(roi_text)
            except:
                pass

        roi_offset_text = self.roi_offset_edit.text()
        if roi_offset_text:
            try:
                settings.algorithm.roi_offset = eval(roi_offset_text)
            except:
                pass

        settings.algorithm.threshold = self.threshold_spin.value()

        # 动作设置
        settings.action.target = self.target_edit.text()
        target_offset_text = self.target_offset_edit.text()
        if target_offset_text:
            try:
                settings.action.target_offset = eval(target_offset_text)
            except:
                pass

        # 任务流设置
        next_tasks = self.next_edit.toPlainText().strip()
        if next_tasks:
            settings.flow.next_tasks = next_tasks.split('\n')

        interrupt_tasks = self.interrupt_edit.toPlainText().strip()
        if interrupt_tasks:
            settings.flow.interrupt_tasks = interrupt_tasks.split('\n')

        error_tasks = self.on_error_edit.toPlainText().strip()
        if error_tasks:
            settings.flow.error_tasks = error_tasks.split('\n')

        # 时间设置
        settings.timing.rate_limit_ms = self.rate_limit_spin.value()
        settings.timing.timeout_ms = self.timeout_spin.value()
        settings.timing.pre_delay_ms = self.pre_delay_spin.value()
        settings.timing.post_delay_ms = self.post_delay_spin.value()
        settings.timing.pre_freeze_ms = self.pre_freeze_spin.value()
        settings.timing.post_freeze_ms = self.post_freeze_spin.value()

        return settings

    def request_roi_selection(self):
        """请求选择ROI"""
        self.roi_selection_requested.emit()

    def update_roi_from_selection(self, start_pos: QPoint, end_pos: QPoint):
        """根据选择更新ROI设置"""
        if start_pos and end_pos:
            x = min(start_pos.x(), end_pos.x())
            y = min(start_pos.y(), end_pos.y())
            width = abs(end_pos.x() - start_pos.x())
            height = abs(end_pos.y() - start_pos.y())

            # 更新ROI输入框
            roi_text = f"[{x}, {y}, {width}, {height}]"
            self.roi_edit.setText(roi_text)

            # 更新settings对象
            self.settings.algorithm.roi = [x, y, width, height]

    def update_target_from_selection(self, start_pos: QPoint, end_pos: QPoint):
        """根据选择更新Target设置"""
        if start_pos and end_pos:
            x = min(start_pos.x(), end_pos.x())
            y = min(start_pos.y(), end_pos.y())
            width = abs(end_pos.x() - start_pos.x())
            height = abs(end_pos.y() - start_pos.y())

            # 更新Target输入框
            target_text = f"[{x}, {y}, {width}, {height}]"
            self.target_edit.setText(target_text)

            # 更新settings对象
            self.settings.action.target = [x, y, width, height]