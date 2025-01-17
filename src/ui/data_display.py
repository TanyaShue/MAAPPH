import os
from datetime import datetime
from functools import partial

from PySide2.QtCore import QPoint, QRect, Signal, Qt
from PySide2.QtGui import QPixmap, QPainter, QColor, QPen
from PySide2.QtGui import Qt
from PySide2.QtWidgets import (
    QHBoxLayout
)
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu, QPushButton

from src.utils.app_config import Config
from src.utils.maa_controller import MaaController


class InfoPanel(QWidget):
    save_and_edit_next_signal = Signal()
    save_and_edit_interrupt_signal = Signal()
    save_and_edit_on_error_signal = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)

        # 创建垂直布局
        layout = QVBoxLayout(self)

        # 添加三个按钮
        self.button1 = QPushButton("保存并编辑next")
        self.button2 = QPushButton("保存并编辑interrupt")
        self.button3 = QPushButton("保存并编辑on_error")

        # 添加弹性空间，使按钮靠下对齐
        layout.addStretch()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)

        # 设置白色背景
        self.setStyleSheet("background-color: white;")

        # 连接信号
        self.button1.clicked.connect(self.save_and_edit_next)
        self.button2.clicked.connect(self.save_and_edit_interrupt)
        self.button3.clicked.connect(self.save_and_edit_on_error)

    def save_and_edit_next(self):
        self.save_and_edit_next_signal.emit()

    def save_and_edit_interrupt(self):
        self.save_and_edit_interrupt_signal.emit()

    def save_and_edit_on_error(self):
        self.save_and_edit_on_error_signal.emit()

class CoordinateLabel(QLabel):
    roi_selected = Signal(QPoint, QPoint)
    target_selected = Signal(QPoint, QPoint)
    recognition_from_roi_signal = Signal(QPoint, QPoint)
    update_screenshot_path = Signal(str)
    clicked_display = Signal(QPoint)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.end_pos = None
        self.show_coordinates = True
        self.setMouseTracking(True)
        self.is_drawing = False
        self.original_image = None
        self.cropped_image = None
        self.maa_controller = MaaController()
        self.last_screenshot_path = None

        # 创建水平布局来容纳主显示区和信息面板
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 创建主显示区
        self.display_label = QLabel(self)
        self.display_label.setMinimumSize(640, 360)
        self.layout.addWidget(self.display_label)

        # 创建信息面板
        self.info_panel = InfoPanel(self)
        self.layout.addWidget(self.info_panel)

        # 创建上下文菜单
        self.context_menu = QMenu(self)

        # 创建上下文菜单项
        self.set_roi_action = self.context_menu.addAction("设置为ROI")
        self.set_target_action = self.context_menu.addAction("设置为Target")
        self.screenshot_action = self.context_menu.addAction("设置为template(截图并保存为template)")
        self.recognition_action = self.context_menu.addAction("识别为expected")

        # 连接菜单动作到相应的处理函数
        self.set_roi_action.triggered.connect(self.set_roi)
        self.set_target_action.triggered.connect(self.set_target)
        self.screenshot_action.triggered.connect(self.take_screenshot)
        self.recognition_action.triggered.connect(self.recognition_from_roi)

    def mousePressEvent(self, event):
        if self.show_coordinates and self.pixmap():
            if event.button() == Qt.LeftButton:
                # 右键开始绘制
                self.is_drawing = True
                self.start_pos = self._convert_coordinates(event.pos())
                self.end_pos = None
                self.update()
            elif event.button() == Qt.RightButton:
                # 左键显示菜单
                self.context_menu.popup(self.mapToGlobal(event.pos()))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.show_coordinates and self.pixmap() and event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.end_pos = self._convert_coordinates(event.pos())
            self.update()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.show_coordinates and self.pixmap() and self.is_drawing:
            self.end_pos = self._convert_coordinates(event.pos())
            self.update()
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.start_pos == self.end_pos:
                # self.maa_controller.click(self.start_pos.x(), self.start_pos.y())
                self.clicked_display.emit(self.start_pos)
        super().mouseDoubleClickEvent(event)

    def set_roi(self):
        """打印ROI坐标"""
        if self.start_pos and self.end_pos:
            self.roi_selected.emit(self.start_pos, self.end_pos)

    def set_target(self):
        """打印target坐标"""
        if self.start_pos and self.end_pos:
            self.target_selected.emit(self.start_pos, self.end_pos)

    def _convert_coordinates(self, pos):
        """Convert coordinates to 1280x720 scale"""
        if not self.pixmap():
            return QPoint(0, 0)

        current_width = self.pixmap().width()
        current_height = self.pixmap().height()
        target_width = 1280
        target_height = 720

        scaled_x = int((pos.x() / current_width) * target_width)
        scaled_y = int((pos.y() / current_height) * target_height)

        # Ensure coordinates are within bounds
        scaled_x = max(0, min(scaled_x, target_width))
        scaled_y = max(0, min(scaled_y, target_height))

        return QPoint(scaled_x, scaled_y)

    def take_screenshot(self):
        """Take screenshot of selected region"""
        if not self.original_image or not self.start_pos or not self.end_pos:
            return None

        # Convert coordinates to original image scale
        orig_width = self.original_image.width()
        orig_height = self.original_image.height()

        start_x = int((self.start_pos.x() * orig_width) / 1280)
        start_y = int((self.start_pos.y() * orig_height) / 720)
        end_x = int((self.end_pos.x() * orig_width) / 1280)
        end_y = int((self.end_pos.y() * orig_height) / 720)

        # Ensure correct order of coordinates
        x = min(start_x, end_x)
        y = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)

        # Convert QImage to QPixmap for cropping
        pixmap = QPixmap.fromImage(self.original_image)
        # Crop the image
        cropped = pixmap.copy(QRect(x, y, width, height))

        # Save with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_dir = os.getcwd()
        config_path = os.path.join(current_dir, "config", "app_config.json")
        app_config = Config.from_file(config_path)
        resource_path = app_config.maa_resource_path
        image_path=os.path.join(f'template\screenshot_{timestamp}.png')
        save_path = os.path.join(resource_path, "image",image_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 确保目录存在
        cropped.save(save_path)

        # filepath = f'img/screenshot_{timestamp}.png'
        # cropped.save(filepath)
        # print(f"Screenshot saved to {filepath}")
        self.cropped_image = cropped  # Store as QPixmap
        self.last_screenshot_path = save_path
        self.update()
        self.update_screenshot_path.emit(image_path)
        # return image_path

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.show_coordinates:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate text position
        x = self.width() - 300  # Offset from right edge
        y = 20  # Initial offset from top

        # Draw coordinates
        if self.start_pos:
            text_lines = [f"起点: ({self.start_pos.x()}, {self.start_pos.y()})"]
            if self.end_pos:
                text_lines.append(f"终点: ({self.end_pos.x()}, {self.end_pos.y()})")
                width = abs(self.end_pos.x() - self.start_pos.x())
                height = abs(self.end_pos.y() - self.start_pos.y())
                text_lines.append(f"roi:[{self.start_pos.x()}, {self.start_pos.y()}, {width}, {height}]")

            if self.last_screenshot_path:
                text_lines.append(f"已保存: {self.last_screenshot_path}")

            # Draw text with outline
            for line in text_lines:
                # Draw black outline
                painter.setPen(QColor(0, 0, 0))
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        painter.drawText(x + dx, y + dy, line)

                # Draw white text
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(x, y, line)
                y += 20

        # Draw selection rectangle
        if self.start_pos and self.end_pos and self.pixmap():
            current_width = self.pixmap().width()
            current_height = self.pixmap().height()

            start_x = (self.start_pos.x() * current_width) / 1280
            start_y = (self.start_pos.y() * current_height) / 720
            end_x = (self.end_pos.x() * current_width) / 1280
            end_y = (self.end_pos.y() * current_height) / 720

            painter.setPen(QPen(QColor(0, 255, 0), 2))
            painter.setBrush(QColor(0, 255, 0, 50))
            painter.drawRect(min(start_x, end_x), min(start_y, end_y),
                             abs(end_x - start_x), abs(end_y - start_y))

        # Draw cropped image preview
        if self.cropped_image:
            preview_width = 160  # Preview width
            preview_height = int(preview_width * self.cropped_image.height() / self.cropped_image.width())
            preview_x = self.width() - preview_width - 20
            preview_y = y + 10  # Position below the text

            # Scale the QPixmap
            preview = self.cropped_image.scaled(preview_width, preview_height,
                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Draw the preview QPixmap
            painter.drawPixmap(preview_x, preview_y, preview)

            # Draw border around preview
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(preview_x, preview_y, preview.width(), preview.height())

    def recognition_from_roi(self):
        if self.start_pos and self.end_pos:
            self.recognition_from_roi_signal.emit(self.start_pos, self.end_pos)

class DataDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Control Buttons Layout
        button_layout = QHBoxLayout()
        buttons = ["刷新", "获取roi(开)", "区域截图","设置"]
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            if btn_text == "刷新":
                btn.clicked.connect(self.refresh_screen)
            elif btn_text == "获取roi(开)":
                btn.clicked.connect(partial(self.toggle_roi_mode, btn))
            elif btn_text == "区域截图":
                btn.clicked.connect(self.take_roi_screenshot)
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)

        # Screen Display
        self.screen_label = CoordinateLabel()
        self.screen_label.setMinimumSize(640, 360)
        layout.addWidget(self.screen_label)

        # ADB Connection
        self.adb_connection = MaaController()

        # Initial screen refresh
        # self.refresh_screen()

    def toggle_roi_mode(self,button):
        self.screen_label.show_coordinates = not self.screen_label.show_coordinates
        self.screen_label.start_pos = None
        self.screen_label.end_pos = None
        self.screen_label.cropped_image = None
        self.screen_label.last_screenshot_path = None
        self.screen_label.update()

        # 更新按钮文本
        if self.screen_label.show_coordinates:
            button.setText("获取roi(开)")
        else:
            button.setText("获取roi(关)")

    def take_roi_screenshot(self):
        self.screen_label.take_screenshot()

    def refresh_screen(self):
        """
        Capture and display device screen
        """
        image = self.adb_connection.get_screen_capture()
        if image:
            self.screen_label.original_image = image  # Store original QImage
            pixmap = QPixmap.fromImage(image)
            self.screen_label.setPixmap(pixmap.scaled(
                self.screen_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))