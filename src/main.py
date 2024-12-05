import sys
import traceback
from PySide2.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow


def main():
    # 设置全局异常捕获
    # sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()