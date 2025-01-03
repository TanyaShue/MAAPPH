from typing import Optional, List, Dict, Any
from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.custom_recognition import CustomRecognition
from maa.notification_handler import NotificationHandler, NotificationType


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
        self.tasker: Optional[Tasker] = None
        self.user_path: str = "./"
        self._initialized = True

    def initialize(self, user_path: str = "./") -> bool:
        """
        Initialize MAA framework with the given user path
        Returns True if initialization successful, False otherwise
        """
        try:
            self.user_path = user_path
            Toolkit.init_option(user_path)

            # Initialize Resource
            self.resource = Resource()
            res_job = self.resource.post_path("sample/resource")
            res_job.wait()

            # Find and connect to ADB device
            adb_devices = Toolkit.find_adb_devices()
            if not adb_devices:
                print("No ADB device found.")
                return False

            device = adb_devices[0]
            self.controller = AdbController(
                adb_path=device.adb_path,
                address=device.address,
                screencap_methods=device.screencap_methods,
                input_methods=device.input_methods,
                config=device.config,
            )
            self.controller.post_connection().wait()

            # Initialize Tasker
            self.tasker = Tasker()
            self.tasker.bind(self.resource, self.controller)

            return self.tasker.inited

        except Exception as e:
            print(f"Failed to initialize MAA: {str(e)}")
            return False

    def register_custom_recognition(self, name: str, recognition: CustomRecognition) -> None:
        """Register a custom recognition handler"""
        if self.resource:
            self.resource.register_custom_recognition(name, recognition)

    def run_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """Run a pipeline and return the task details"""
        if not self.tasker:
            raise RuntimeError("MAA not initialized")

        task_detail = self.tasker.post_pipeline(pipeline_name).wait().get()
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

    def set_notification_handler(self, handler: NotificationHandler) -> None:
        """Set a custom notification handler for the tasker"""
        if self.tasker:
            self.tasker = Tasker(notification_handler=handler)
            if self.resource and self.controller:
                self.tasker.bind(self.resource, self.controller)

    @property
    def is_initialized(self) -> bool:
        """Check if the MAA framework is initialized"""
        return bool(self.tasker and self.tasker.inited)


# Usage example:
"""
# Get singleton instance
maa = MaaController()

# Initialize with custom path
if not maa.is_initialized:
    success = maa.initialize(user_path="./custom/path")
    if not success:
        print("Failed to initialize MAA")
        exit()

# Run a pipeline
task_result = maa.run_pipeline("StartUpAndClickButton")

# Perform actions
maa.click(100, 200)
maa.swipe(10, 20, 100, 100, 200)
maa.take_screenshot()

# Register custom recognition
maa.register_custom_recognition("MyRec", MyRecognition())

# Set custom notification handler
maa.set_notification_handler(MyNotificationHandler())
"""