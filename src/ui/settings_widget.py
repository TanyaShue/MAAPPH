from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QCheckBox, QSpinBox, QLineEdit, QTextEdit, QScrollArea,
                             QDoubleSpinBox, QFrame)


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # scroll.setFixedHeight(600)  # 固定高度

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        # 标题
        settings_title = QLabel("节点详情")
        settings_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(settings_title)

        # 基础配置区域
        basic_group = self.create_group("基础配置")
        layout.addWidget(basic_group)

        # 算法配置区域
        algo_group = self.create_group("算法配置")
        layout.addWidget(algo_group)

        # 动作配置区域
        action_group = self.create_group("动作配置")
        layout.addWidget(action_group)

        # 任务流配置区域
        flow_group = self.create_group("任务流配置")
        layout.addWidget(flow_group)

        # 时间配置区域
        timing_group = self.create_group("时间配置")
        layout.addWidget(timing_group)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_group(self, title):
        group = QFrame()
        group.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(group)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)

        if title == "基础配置":
            self.add_basic_settings(layout)
        elif title == "算法配置":
            self.add_algo_settings(layout)
        elif title == "动作配置":
            self.add_action_settings(layout)
        elif title == "任务流配置":
            self.add_flow_settings(layout)
        elif title == "时间配置":
            self.add_timing_settings(layout)

        return group

    def create_row(self, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(150)  # 固定标签宽度
        row.addWidget(label)
        row.addWidget(widget)
        return row

    def add_basic_settings(self, layout):
        # 识别算法类型
        recognition_combo = QComboBox()
        recognition_combo.addItems([
            "DirectHit", "TemplateMatch", "FeatureMatch", "ColorMatch",
            "OCR", "NeuralNetworkClassify", "NeuralNetworkDetect", "Custom"
        ])
        layout.addLayout(self.create_row("识别算法类型:", recognition_combo))

        # 执行动作
        action_combo = QComboBox()
        action_combo.addItems([
            "DoNothing", "Click", "Swipe", "MultiSwipe", "Key",
            "InputText", "StartApp", "StopApp", "StopTask", "Command", "Custom"
        ])
        layout.addLayout(self.create_row("执行动作:", action_combo))

        # 基础复选框选项
        enabled_check = QCheckBox("启用任务")
        enabled_check.setChecked(True)
        layout.addWidget(enabled_check)

        focus_check = QCheckBox("关注任务")
        layout.addWidget(focus_check)

        inverse_check = QCheckBox("反转识别结果")
        layout.addWidget(inverse_check)

    def add_algo_settings(self, layout):
        # ROI 设置
        roi_edit = QLineEdit()
        roi_edit.setPlaceholderText("[x, y, w, h]")
        layout.addLayout(self.create_row("识别区域(ROI):", roi_edit))

        # ROI Offset
        roi_offset_edit = QLineEdit()
        roi_offset_edit.setPlaceholderText("[x, y, w, h]")
        layout.addLayout(self.create_row("ROI偏移:", roi_offset_edit))

        # 阈值
        threshold_spin = QDoubleSpinBox()
        threshold_spin.setRange(0, 1)
        threshold_spin.setSingleStep(0.1)
        threshold_spin.setValue(0.7)
        layout.addLayout(self.create_row("匹配阈值:", threshold_spin))

    def add_action_settings(self, layout):
        # Target
        target_edit = QLineEdit()
        target_edit.setPlaceholderText("true/任务名/[x,y,w,h]")
        layout.addLayout(self.create_row("目标位置:", target_edit))

        # Target Offset
        target_offset_edit = QLineEdit()
        target_offset_edit.setPlaceholderText("[x, y, w, h]")
        layout.addLayout(self.create_row("目标偏移:", target_offset_edit))

    def add_flow_settings(self, layout):
        # Next Tasks
        next_edit = QTextEdit()
        next_edit.setPlaceholderText("输入任务名称，每行一个")
        next_edit.setMaximumHeight(80)
        layout.addLayout(self.create_row("下一个任务:", next_edit))

        # Interrupt Tasks
        interrupt_edit = QTextEdit()
        interrupt_edit.setPlaceholderText("输入中断任务名称，每行一个")
        interrupt_edit.setMaximumHeight(80)
        layout.addLayout(self.create_row("中断任务:", interrupt_edit))

        # On Error Tasks
        on_error_edit = QTextEdit()
        on_error_edit.setPlaceholderText("输入错误处理任务名称，每行一个")
        on_error_edit.setMaximumHeight(80)
        layout.addLayout(self.create_row("错误处理任务:", on_error_edit))

    def add_timing_settings(self, layout):
        # Rate Limit
        rate_limit_spin = QSpinBox()
        rate_limit_spin.setRange(0, 10000)
        rate_limit_spin.setValue(1000)
        rate_limit_spin.setSingleStep(100)
        layout.addLayout(self.create_row("识别速率限制(ms):", rate_limit_spin))

        # Timeout
        timeout_spin = QSpinBox()
        timeout_spin.setRange(0, 60000)
        timeout_spin.setValue(20000)
        timeout_spin.setSingleStep(1000)
        layout.addLayout(self.create_row("超时时间(ms):", timeout_spin))

        # Pre Delay
        pre_delay_spin = QSpinBox()
        pre_delay_spin.setRange(0, 5000)
        pre_delay_spin.setValue(200)
        layout.addLayout(self.create_row("执行前延迟(ms):", pre_delay_spin))

        # Post Delay
        post_delay_spin = QSpinBox()
        post_delay_spin.setRange(0, 5000)
        post_delay_spin.setValue(200)
        layout.addLayout(self.create_row("执行后延迟(ms):", post_delay_spin))

        # Pre Wait Freezes
        pre_freeze_spin = QSpinBox()
        pre_freeze_spin.setRange(0, 5000)
        layout.addLayout(self.create_row("执行前等待画面静止(ms):", pre_freeze_spin))

        # Post Wait Freezes
        post_freeze_spin = QSpinBox()
        post_freeze_spin.setRange(0, 5000)
        layout.addLayout(self.create_row("执行后等待画面静止(ms):", post_freeze_spin))


