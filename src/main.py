import sys
import traceback
from PySide2.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow


def exception_hook(exctype, value, tb):
    """全局异常捕获"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(error_msg)

    # 显示错误对话框
    app = QApplication.instance()
    if app:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("发生了一个意外错误")
        error_dialog.setDetailedText(error_msg)
        error_dialog.setWindowTitle("错误")
        error_dialog.exec_()


def main():
    # 设置全局异常捕获
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()