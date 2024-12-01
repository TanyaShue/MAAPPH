from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QCheckBox, QSlider, QComboBox
)
from PySide2.QtCore import Qt


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        settings_title = QLabel("系统设置")
        layout.addWidget(settings_title)

        # 示例设置项
        theme_label = QLabel("主题选择")
        theme_combo = QComboBox()
        theme_combo.addItems(["浅色", "深色"])

        auto_save_check = QCheckBox("自动保存")

        performance_label = QLabel("性能设置")
        performance_slider = QSlider(Qt.Horizontal)
        performance_slider.setRange(0, 100)

        layout.addWidget(theme_label)
        layout.addWidget(theme_combo)
        layout.addWidget(auto_save_check)
        layout.addWidget(performance_label)
        layout.addWidget(performance_slider)

        layout.addStretch()