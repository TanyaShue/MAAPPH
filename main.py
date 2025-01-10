from maa import Library  # 导入 maa 库 不要删除,容易发生兼容问题
from src.ui.main_window import MainWindow
import sys
import asyncio
from PySide2.QtWidgets import QApplication
from qasync import QEventLoop


async def main():
    app = QApplication(sys.argv)

    # 使用 qasync 的事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # 创建主窗口并显示
    main_window = MainWindow()
    main_window.show()

    # 在事件循环中运行程序
    with loop:
        loop.run_forever()


if __name__ == '__main__':
    asyncio.run(main())
