from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem
)


class DataDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("数据总览")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["任务ID", "任务名称", "状态", "进度"])

        # 示例数据
        sample_data = [
            ["001", "数据处理", "进行中", "60%"],
            ["002", "报告生成", "已完成", "100%"],
            ["003", "数据分析", "未开始", "0%"]
        ]

        self.table.setRowCount(len(sample_data))
        for row, row_data in enumerate(sample_data):
            for col, value in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(value))

        layout.addWidget(self.table)