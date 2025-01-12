from dataclasses import dataclass
from typing import List, Optional

from PySide2.QtCore import QPoint
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                               QCheckBox, QSpinBox, QLineEdit, QTextEdit, QScrollArea,
                               QDoubleSpinBox, QFrame)

from src.node_graph.graph_widget import MyNode
from src.utils.maa_controller import MaaController


# 基础节点设置
@dataclass
class BasicSettings:
    recognition: str = "DirectHit"
    action: str = "DoNothing"
    enabled: bool = True
    focus: bool = False
    inverse: bool = False

# 节点匹配范围设置
@dataclass
class AlgorithmSettings:
    roi: List[int] = None  # [x, y, w, h]
    roi_offset: List[int] = None  # [x, y, w, h]
    threshold: float = 0.7

# 节点匹配目标设置
@dataclass
class TargetSettings:
    expected: str = ""
    target: str = ""
    template: str =""
    target_offset: List[int] = None
# 节点动作目标设置
@dataclass
class ActionSettings:
    target: str = ""  # can be "true", task name, or [x,y,w,h]
    target_offset: List[int] = None  # [x, y, w, h]

# 节点流程设置
@dataclass
class FlowSettings:
    next: List[str] = None
    interrupt: List[str] = None
    on_error: List[str] = None

# 节点时间设置
@dataclass
class TimingSettings:
    rate_limit: int = 1000
    timeout: int = 20000
    pre_delay: int = 200
    post_delay: int = 200
    pre_wait_freezes: int = 0
    post_wait_freezes: int = 0


class TaskNode:
    def __init__(self):
        self.basic = BasicSettings()
        self.algorithm = AlgorithmSettings()
        self.action = ActionSettings()
        self.flow = FlowSettings()
        self.timing = TimingSettings()
        self.target = TargetSettings()


class NoteWidget(QWidget):

    def __init__(self, settings: Optional[TaskNode] = None):
        super().__init__()
        self.node = None
        self.main_layout = None
        self.settings_title = None
        self.title_name :str = "默认节点"
        self.settings = settings or TaskNode()
        self.init_ui()
        self.load_settings()
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
        self.settings_title = QLabel(f"节点详情--{self.title_name}")
        self.settings_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.settings_title)

        # 添加各个配置组
        groups = [
            ("基础配置", self.create_basic_group),
            ("算法配置", self.create_algo_group),
            ("目标配置", self.create_target_group),
            ("动作配置", self.create_action_group),
            ("任务流配置", self.create_flow_group),
            ("时间配置", self.create_timing_group)
        ]

        for title, create_func in groups:
            group = create_func()
            group.setFrameStyle(QFrame.StyledPanel)
            layout.addWidget(group)

        scroll.setWidget(content_widget)
        setting_layout.addWidget(scroll)
        self.main_layout=setting_layout

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

        self.expected_target_edit = QLineEdit()
        self.expected_target_offset_edit = QLineEdit()

        self.expected_target_edit.setPlaceholderText("匹配字符")
        self.expected_target_offset_edit.setPlaceholderText("图片名称")

        layout.addLayout(self.create_row("expected:", self.expected_target_edit))
        layout.addLayout(self.create_row("template:", self.expected_target_offset_edit))

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
        """从 TaskNode 加载设置到 UI"""
        # QLabel(f"节点详情--{self.title_name}")
        self.settings_title.setText(f"节点详情--{self.title_name}")
        # 基础设置
        self.recognition_combo.setCurrentText(self.settings.basic.recognition)
        self.action_combo.setCurrentText(self.settings.basic.action)
        self.enabled_check.setChecked(self.settings.basic.enabled)
        self.focus_check.setChecked(self.settings.basic.focus)
        self.inverse_check.setChecked(self.settings.basic.inverse)

        # 算法设置
        if self.settings.algorithm.roi:
            self.roi_edit.setText(str(self.settings.algorithm.roi))
        if self.settings.algorithm.roi_offset:
            self.roi_offset_edit.setText(str(self.settings.algorithm.roi_offset))
        self.threshold_spin.setValue(self.settings.algorithm.threshold)

        # 目标设置
        if self.settings.target.expected:
            self.expected_target_edit.setText(str(self.settings.target.expected))
        if self.settings.target.target:
            self.target_edit.setText(str(self.settings.target.target))
        if self.settings.target.target_offset:
            self.target_offset_edit.setText(str(self.settings.target.target_offset))

        # 动作设置
        self.target_edit.setText(str(self.settings.action.target))
        if self.settings.action.target_offset:
            self.target_offset_edit.setText(str(self.settings.action.target_offset))

        # 任务流设置
        if self.settings.flow.next:
            self.next_edit.setText('\n'.join(self.settings.flow.next))
        if self.settings.flow.interrupt:
            self.interrupt_edit.setText('\n'.join(self.settings.flow.interrupt))
        if self.settings.flow.on_error:
            self.on_error_edit.setText('\n'.join(self.settings.flow.on_error))

        # 时间设置
        self.rate_limit_spin.setValue(self.settings.timing.rate_limit)
        self.timeout_spin.setValue(self.settings.timing.timeout)
        self.pre_delay_spin.setValue(self.settings.timing.pre_delay)
        self.post_delay_spin.setValue(self.settings.timing.post_delay)
        self.pre_freeze_spin.setValue(self.settings.timing.pre_wait_freezes)
        self.post_freeze_spin.setValue(self.settings.timing.post_wait_freezes)

    def get_settings(self) -> TaskNode:
        """从 UI 获取设置并返回 TaskNode 对象"""
        settings = TaskNode()

        # 基础设置
        settings.basic.recognition = self.recognition_combo.currentText()
        settings.basic.action = self.action_combo.currentText()
        settings.basic.enabled = self.enabled_check.isChecked()
        settings.basic.focus = self.focus_check.isChecked()
        settings.basic.inverse = self.inverse_check.isChecked()

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
            settings.flow.next = next_tasks.split('\n')

        interrupt_tasks = self.interrupt_edit.toPlainText().strip()
        if interrupt_tasks:
            settings.flow.interrupt = interrupt_tasks.split('\n')

        error_tasks = self.on_error_edit.toPlainText().strip()
        if error_tasks:
            settings.flow.on_error = error_tasks.split('\n')

        # 时间设置
        settings.timing.rate_limit = self.rate_limit_spin.value()
        settings.timing.timeout = self.timeout_spin.value()
        settings.timing.pre_delay = self.pre_delay_spin.value()
        settings.timing.post_delay = self.post_delay_spin.value()
        settings.timing.pre_wait_freezes = self.pre_freeze_spin.value()
        settings.timing.post_wait_freezes = self.post_freeze_spin.value()

        return settings

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

                print(results.nodes[0].recognition.best_result)
                self.expected_target_edit.setText(results.nodes[0].recognition.best_result.text)
            except Exception :
                self.expected_target_edit.setText("")

                self.expected_target_edit.setPlaceholderText("识别失败")

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
        self.title_name = node.NODE_NAME
        note_data = node.note_data
        try:
            # Map note_data to TaskNode attributes
            self.settings.basic.recognition = note_data.get('recognition', self.settings.basic.recognition)
            self.settings.basic.action = note_data.get('action', self.settings.basic.action)
            self.settings.basic.enabled = note_data.get('enabled', self.settings.basic.enabled)
            self.settings.basic.focus = note_data.get('focus', self.settings.basic.focus)
            self.settings.basic.inverse = note_data.get('inverse', self.settings.basic.inverse)

            self.settings.algorithm.roi = note_data.get('roi', self.settings.algorithm.roi)
            self.settings.algorithm.roi_offset = note_data.get('roi_offset', self.settings.algorithm.roi_offset)
            self.settings.algorithm.threshold = note_data.get('threshold', self.settings.algorithm.threshold)

            self.settings.target.expected = note_data.get('expected', self.settings.target.expected)
            self.settings.target.target = note_data.get('target', self.settings.target.target)
            self.settings.target.target_offset = note_data.get('target_offset', self.settings.target.target_offset)

            self.settings.action.target = note_data.get('custom_action', note_data.get('target', self.settings.action.target))
            self.settings.action.target_offset = note_data.get('target_offset', self.settings.action.target_offset)

            self.settings.flow.next = note_data.get('next', self.settings.flow.next)
            self.settings.flow.interrupt = note_data.get('interrupt', self.settings.flow.interrupt)
            self.settings.flow.on_error = note_data.get('on_error', self.settings.flow.on_error)

            self.settings.timing.rate_limit = note_data.get('rate_limit', self.settings.timing.rate_limit)
            self.settings.timing.timeout = note_data.get('timeout', self.settings.timing.timeout)
            self.settings.timing.pre_delay = note_data.get('pre_delay', self.settings.timing.pre_delay)
            self.settings.timing.post_delay = note_data.get('post_delay', self.settings.timing.post_delay)
            self.settings.timing.pre_wait_freezes = note_data.get('pre_wait_freezes', self.settings.timing.pre_wait_freezes)
            self.settings.timing.post_wait_freezes = note_data.get('post_wait_freezes', self.settings.timing.post_wait_freezes)
        except Exception as e:
            print(f"Error loading settings from node: {e}")
        # Update UI or other components
        # 4. 重新初始化UI并加载设置
        self.init_ui()
        self.load_settings()