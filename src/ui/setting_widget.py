import os
from functools import partial

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QScrollArea, QFrame

from src.utils.app_config import AdbConfig, Config


class SettingWidget(QWidget):
    # 信号定义
    connect_adb_signal = Signal(AdbConfig, str)
    connect_resource_signal = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        current_dir = os.getcwd()
        self.config_path = os.path.join(current_dir, "config", "app_config.json")
        self.app_config = Config.from_file(self.config_path)

        # ADB 设置组
        adb_group_layout = QVBoxLayout()
        adb_group_title = QLabel("ADB 设置")
        adb_group_layout.addWidget(adb_group_title)

        # ADB Host Input
        host_layout = QHBoxLayout()
        host_label = QLabel("主机地址:")
        self.host_input = QLineEdit(self.app_config.adb_config.adb_path)
        self.host_input.textChanged.connect(self.update_adb_config)  # 添加信号槽
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        adb_group_layout.addLayout(host_layout)

        # ADB Port Input
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QLineEdit(self.app_config.adb_config.adb_address)
        self.port_input.textChanged.connect(self.update_adb_config)  # 添加信号槽
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        adb_group_layout.addLayout(port_layout)

        # Connect Device Button
        connect_adb_btn = QPushButton("连接设备")
        connect_adb_btn.clicked.connect(self.connect_adb)
        adb_group_layout.addWidget(connect_adb_btn)

        adb_group_layout.addStretch(0)  # <--- Add this line
        layout.addLayout(adb_group_layout)

        # 资源路径组
        resource_group_layout = QVBoxLayout()
        resource_group_title = QLabel("资源路径设置")
        resource_group_layout.addWidget(resource_group_title)

        # Resource Path Input
        resource_layout = QHBoxLayout()
        resource_label = QLabel("资源路径:")
        self.resource_input = QLineEdit(self.app_config.maa_resource_path)
        self.resource_input.textChanged.connect(self.update_resource_path)  # 添加信号槽
        resource_layout.addWidget(resource_label)
        resource_layout.addWidget(self.resource_input)
        resource_group_layout.addLayout(resource_layout)

        # Connect Resource Button
        connect_resource_btn = QPushButton("连接资源")
        connect_resource_btn.clicked.connect(self.connect_resource)
        resource_group_layout.addWidget(connect_resource_btn)

        # Scroll Area for JSON files
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(400)  # 限定高度

        self.json_files_widget = QWidget()
        self.json_files_layout = QVBoxLayout(self.json_files_widget)
        self.scroll_area.setWidget(self.json_files_widget)

        resource_group_layout.addWidget(self.scroll_area)

        resource_group_layout.addStretch(0)  # <--- Add this line
        layout.addLayout(resource_group_layout)

        layout.addStretch(1)  # <--- Add this line

    def update_adb_config(self):
        """更新 ADB 设置并保存到配置文件"""
        self.app_config.adb_config.adb_path = self.host_input.text()
        self.app_config.adb_config.adb_address = self.port_input.text()
        self.app_config.to_file(self.config_path)

    def update_resource_path(self):
        """更新资源路径并保存到配置文件"""
        self.app_config.maa_resource_path = self.resource_input.text()
        self.app_config.to_file(self.config_path)

    def connect_adb(self):
        host = self.host_input.text()
        port = self.port_input.text()
        adb_config = AdbConfig(
            adb_path=host,
            adb_address=port,
            screencap_methods=18446744073709551559,
            input_methods=18446744073709551607,
            config={}
        )
        user_path = "./"
        self.connect_adb_signal.emit(adb_config, user_path)

    def connect_resource(self):
        resource_path = self.resource_input.text()
        self.connect_resource_signal.emit(resource_path)
        pipeline_dir = os.path.join(resource_path, "pipeline")
        if os.path.exists(pipeline_dir) and os.path.isdir(pipeline_dir):
            self.display_json_files(pipeline_dir)

    def display_json_files(self, pipeline_dir):
        """显示 pipeline 文件夹下的所有 JSON 文件"""
        # 清空布局
        for i in reversed(range(self.json_files_layout.count())):
            item = self.json_files_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 添加 JSON 文件
        json_files = [f for f in os.listdir(pipeline_dir) if f.endswith(".json")]
        for file_name in json_files:
            file_layout = QHBoxLayout()
            file_label = QLabel(file_name)
            open_button = QPushButton("打开")
            open_button.clicked.connect(partial(self.open_in_nodegraph, file_name))
            file_layout.addWidget(file_label)
            file_layout.addStretch()
            file_layout.addWidget(open_button)
            container = QWidget()
            container.setLayout(file_layout)
            self.json_files_layout.setSpacing(1)
            self.json_files_layout.setContentsMargins(0, 0, 0, 0)
            self.json_files_layout.addWidget(container)

    def open_in_nodegraph(self, file_name):
        """打开 JSON 文件的占位方法"""
        print(f"打开文件: {file_name}")
