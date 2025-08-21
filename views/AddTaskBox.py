from PyQt6.QtCore import QTime, QDate, QDateTime
from PyQt6.QtWidgets import QHBoxLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, TimePicker, CalendarPicker, ComboBox, BodyLabel


class AddTaskBox(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('新增待办事项')

        self.input_field = LineEdit()

        self.input_field.setPlaceholderText('任务内容...')
        self.input_field.setClearButtonEnabled(True)

        self.datetime_layout = QHBoxLayout()
        self.time_edit = TimePicker()
        self.date_edit = CalendarPicker()
        self.time_edit.setTime(QTime.currentTime())
        self.date_edit.setDate(QDate.currentDate())
        self.datetime_layout.addWidget(self.date_edit)
        self.datetime_layout.addWidget(self.time_edit)

        self.repeat_layout = QHBoxLayout()
        self.repeat_combo = ComboBox()
        self.repeat_combo.addItems(["不重复", "每天", "每周"])
        self.repeat_layout.addWidget(BodyLabel("重复周期:"))
        self.repeat_layout.addWidget(self.repeat_combo)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.input_field)
        self.viewLayout.addLayout(self.datetime_layout)
        self.viewLayout.addLayout(self.repeat_layout)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)

        self.yesButton.setText('确认')
        self.cancelButton.setText('取消')

    def get_data(self):
        return (
            self.input_field.text().strip(),
            QDateTime(self.date_edit.date, self.time_edit.time),  # ✅ 修复
            self.repeat_combo.currentText()
        )
