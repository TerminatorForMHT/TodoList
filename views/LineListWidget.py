from PyQt6.QtWidgets import QListWidget
from PyQt6.QtGui import QPainter, QColor

from qss.qss import task_style_sheet


class LineListWidget(QListWidget):
    """QListWidget 空列表也显示横线"""

    def __init__(self, parent=None, row_height=40):
        super().__init__(parent)
        self.row_height = row_height
        self.setSpacing(0)
        self.setStyleSheet(task_style_sheet)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        color = QColor(192, 192, 192)
        painter.setPen(color)

        count = self.count()
        if count > 0:
            # 任务行的横线
            for i in range(count):
                rect = self.visualItemRect(self.item(i))
                y = rect.bottom()
                painter.drawLine(rect.left(), y, rect.right(), y)
        else:
            # 空列表时绘制多行横线
            height = self.viewport().height()
            y = 0
            while y < height:
                painter.drawLine(0, y + self.row_height - 1, self.viewport().width(), y + self.row_height - 1)
                y += self.row_height
