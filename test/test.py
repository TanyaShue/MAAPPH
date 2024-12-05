from Qt.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit,
    QCheckBox, QPushButton, QFormLayout
)
from Qt.QtCore import Qt

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Widget with Properties")

        # Layout for the widget
        self.layout = QVBoxLayout(self)

        # Create and add components based on provided properties
        self.create_recognition_section()
        self.create_action_section()
        self.create_text_input_section("Rate Limit (ms):", "1000", "rate_limit")
        self.create_text_input_section("Timeout (ms):", "20000", "timeout")
        self.create_checkbox_section("Inverse Recognition", "inverse", False)
        self.create_checkbox_section("Enable Task", "enabled", True)

        # Add an apply button for testing
        self.apply_button = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_settings)
        self.layout.addWidget(self.apply_button)

        # Set main layout
        self.setLayout(self.layout)

    def create_recognition_section(self):
        # Recognition combo box
        label = QLabel("Recognition:")
        self.recognition_combo = QComboBox()
        self.recognition_combo.addItems([
            "DirectHit", "TemplateMatch", "FeatureMatch",
            "ColorMatch", "OCR", "NeuralNetworkClassify",
            "NeuralNetworkDetect", "Custom"
        ])
        self.recognition_combo.setCurrentText("DirectHit")
        self.layout.addWidget(label)
        self.layout.addWidget(self.recognition_combo)

    def create_action_section(self):
        # Action combo box
        label = QLabel("Actions:")
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "DoNothing", "Click", "Swipe", "Key",
            "InputText", "StartApp", "StopApp",
            "StopTask", "Custom"
        ])
        self.action_combo.setCurrentText("DoNothing")
        self.layout.addWidget(label)
        self.layout.addWidget(self.action_combo)

    def create_text_input_section(self, label_text, placeholder, attr_name):
        # Text input with label
        label = QLabel(label_text)
        text_input = QLineEdit()
        text_input.setPlaceholderText(placeholder)
        setattr(self, f"{attr_name}_input", text_input)
        self.layout.addWidget(label)
        self.layout.addWidget(text_input)

    def create_checkbox_section(self, label_text, attr_name, default_state):
        # Checkbox with label
        checkbox = QCheckBox(label_text)
        checkbox.setChecked(default_state)
        setattr(self, f"{attr_name}_checkbox", checkbox)
        self.layout.addWidget(checkbox)

    def apply_settings(self):
        # Gather settings and print them
        settings = {
            "recognition": self.recognition_combo.currentText(),
            "action": self.action_combo.currentText(),
            "rate_limit": self.rate_limit_input.text(),
            "timeout": self.timeout_input.text(),
            "inverse": self.inverse_checkbox.isChecked(),
            "enabled": self.enabled_checkbox.isChecked()
        }
        print("Current Settings:", settings)


# Test the widget
if __name__ == "__main__":
    import sys
    from Qt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = CustomWidget()
    widget.show()
    sys.exit(app.exec_())
