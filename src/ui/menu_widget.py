import subprocess
from typing import Optional

from Qt.QtCore import Qt
from Qt.QtGui import QImage
from Qt.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout


class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        menu_title = QLabel("ADB 连接设置")
        layout.addWidget(menu_title)

        # ADB Host Input
        host_layout = QHBoxLayout()
        host_label = QLabel("主机地址:")
        self.host_input = QLineEdit('localhost')
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        layout.addLayout(host_layout)

        # ADB Port Input
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QLineEdit('5555')
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        # Connect Button
        connect_btn = QPushButton("连接设备")
        connect_btn.clicked.connect(self.connect_device)
        layout.addWidget(connect_btn)

        layout.addStretch()

    def connect_device(self):
        host = self.host_input.text()
        port = self.port_input.text()
        # TODO: Implement actual connection logic and signal to main window



class ADBConnection:
    def __init__(self, host: str = '127.0.0.1', port: str = '5555'):
        self.host = host
        self.port = port

    def get_screen_capture(self) -> Optional[QImage]:
        """
        Capture screen from ADB device and return as QImage
        """
        try:
            # Run ADB command to capture screen
            capture_cmd = f'D:\\leidian\\LDPlayer9\\adb.exe -s emulator-5554 shell screencap -p /sdcard/screen.png'
            pull_cmd = f'D:\\leidian\\LDPlayer9\\adb.exe -s emulator-5554 pull /sdcard/screen.png screen.png'

            subprocess.run(capture_cmd, shell=True, check=True)
            subprocess.run(pull_cmd, shell=True, check=True)

            # Read image and convert to QImage
            image = QImage('screen.png')
            return image.scaled(1280, 720, Qt.KeepAspectRatio)
        except Exception as e:
            print(f"ADB Screen Capture Error: {e}")
            return None