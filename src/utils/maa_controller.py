import subprocess
from typing import Optional, Dict, Any

import cv2
from PySide2.QtCore import Qt
from PySide2.QtGui import QImage
from maa.controller import AdbController
from maa.custom_recognition import CustomRecognition
from maa.notification_handler import NotificationHandler
from maa.resource import Resource
from maa.tasker import Tasker
from maa.toolkit import Toolkit
import numpy as np
from src.utils.app_config import AdbConfig


class MaaController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MaaController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Initialize core components
        self.resource: Optional[Resource] = None
        self.controller: Optional[AdbController] = None
        self._tasker: Optional[Tasker] = None
        self.user_path: str = "./"
        self._initialized = True
        self.adb_config = None

    @property
    def tasker(self):
        if self._tasker is None or not self._tasker.inited:
            raise RuntimeError("Tasker is not initialized. Please call initialize_tasker() first.")
        return self._tasker

    def connect_adb(self, user_path: str = "./", adb_config: AdbConfig = None) -> bool:
        """
        Initialize MAA framework with the given user path, resource, and adb config.
        Returns True if initialization successful, False otherwise.
        """
        try:
            self.user_path = user_path
            Toolkit.init_option(user_path)
            self.adb_config = adb_config

            # Find and connect to ADB device
            self.controller = AdbController(
                adb_path=adb_config.adb_path,
                address=adb_config.adb_address,
                screencap_methods=adb_config.screencap_methods,
                input_methods=adb_config.input_methods,
                config=adb_config.config
            )
            self.controller.post_connection().wait()

            self._initialize_tasker_if_ready()

            return True
        except Exception as e:
            print(f"Failed to initialize MAA: {str(e)}")
            return False

    def initialize_tasker(self) -> bool:
        try:
            # Initialize Tasker
            self._tasker = Tasker()
            self._tasker.bind(self.resource, self.controller)
            return self._tasker.inited

        except Exception as e:
            print(f"Failed to initialize Tasker: {str(e)}")
            return False

    def connect_resource(self, resource_path: str = "./sample/resource") -> bool:
        """
        Initialize resources with the given resource path.
        Returns True if initialization successful, False otherwise.
        """
        try:
            # Initialize Resource
            self.resource = Resource()
            res_job = self.resource.post_path(resource_path)
            res_job.wait()

            self._initialize_tasker_if_ready()

            return True
        except Exception as e:
            print(f"Failed to initialize resource: {str(e)}")
            return False

    def _initialize_tasker_if_ready(self):
        """
        Automatically initialize Tasker if both resource and controller are initialized.
        """
        if self.resource is not None and self.controller is not None:
            if self._tasker is None or not self._tasker.inited:
                self.initialize_tasker()


    def get_screen_capture(self):
        """
        Capture screen from ADB device and return as QImage
        """
        try:
            # Run ADB command to capture screen
            capture_cmd = f'{self.adb_config.adb_path} -s {self.adb_config.adb_address} shell screencap -p /sdcard/screen.png'
            pull_cmd = f'{self.adb_config.adb_path} -s {self.adb_config.adb_address} pull /sdcard/screen.png screen.png'

            subprocess.run(capture_cmd, shell=True, check=True)
            subprocess.run(pull_cmd, shell=True, check=True)

            # Read image and convert to QImage
            image = QImage('screen.png')
            return image.scaled(1280, 720, Qt.KeepAspectRatio)
        except Exception as e:
            print(f"ADB Screen Capture Error: {e}")
            return None
        #   不知道为什么闪退,暂时注释
        # 获取缓存图像 (numpy.ndarray)
        # img = self.controller.post_screencap().wait().get()
        # print(f"img type:{type(img)}")
        # print(len(img.shape))
        # if len(img.shape) == 3:
        #     height, width, channel = img.shape
        #     bytes_per_line = channel * width
        #     # 转换为RGB格式
        #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #
        #     # 创建QImage
        #     image = QImage(img.data,width,height,bytes_per_line,QImage.Format_RGB888)
        #     # 保存图像
        #     image.save("screen.png")
        #
        #     # 返回缩放后的图像
        #     return image.scaled(1280, 720, Qt.KeepAspectRatio)
        # else:
        #     print("Invalid image format")
        #     return None

    def register_custom_recognition(self, name: str, recognition: CustomRecognition) -> None:
        """Register a custom recognition handler"""
        if self.resource:
            self.resource.register_custom_recognition(name, recognition)

    def run_pipeline(self, pipeline: str) -> Dict[str, Any]:
        """Run a pipeline and return the task details"""
        if not self.tasker:
            raise RuntimeError("MAA not initialized")

        task_detail = self.tasker.post_pipeline(pipeline).wait().get()
        return task_detail

    def take_screenshot(self) -> None:
        """Take a screenshot using the controller"""
        if self.controller:
            self.controller.post_screencap().wait()

    def click(self, x: int, y: int) -> None:
        """Perform a click action at the specified coordinates"""
        if self.controller:
            self.controller.post_click(x, y).wait()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int) -> None:
        """Perform a swipe action from start to end coordinates"""
        if self.controller:
            self.controller.post_swipe(start_x, start_y, end_x, end_y, duration_ms).wait()

    @property
    def is_initialized(self) -> bool:
        """Check if the MAA framework is initialized"""
        return bool(self.tasker and self.tasker.inited)
