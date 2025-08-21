from PyQt6.QtCore import QTime, QDate, QDateTime
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSystemTrayIcon
from qfluentwidgets import CheckBox, LineEdit, ComboBox, BodyLabel, TimePicker, CalendarPicker


class TodoItemWidget(QWidget):
    """每一行的待办事项控件"""

    def __init__(self, text, remind_time, repeat, done=False, parent=None, save_callback=None):
        super().__init__(parent)

        self.notified = False
        self.save_callback = save_callback  # 传入保存函数

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # 完成状态
        self.checkbox = CheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.stateChanged.connect(self.update_style)
        self.checkbox.stateChanged.connect(self.trigger_save)

        # 任务文字（可编辑）
        self.text_edit = LineEdit()
        self.text_edit.setText(text)
        self.text_edit.textChanged.connect(self.trigger_save)

        # 提醒时间
        self.time_edit = TimePicker()
        self.date_edit = CalendarPicker()

        now = remind_time  # QDateTime

        date = now.date()  # QDate
        time = now.time()  # QTime

        year = date.year()
        month = date.month()
        day = date.day()

        hour = time.hour()
        minute = time.minute()
        second = time.second()

        self.time_edit.setTime(QTime(hour, minute, second))
        self.date_edit.setDate(QDate(year, month, day))

        self.time_edit.timeChanged.connect(self.trigger_save)
        self.date_edit.dateChanged.connect(self.trigger_save)

        # 重复周期
        self.repeat_combo = ComboBox()
        self.repeat_combo.addItems(["不重复", "每天", "每周"])
        self.repeat_combo.setCurrentText(repeat)
        self.repeat_combo.currentTextChanged.connect(self.trigger_save)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_edit, stretch=1)
        layout.addWidget(BodyLabel("提醒:"))
        layout.addWidget(self.date_edit)
        layout.addWidget(self.time_edit)
        layout.addWidget(BodyLabel("重复:"))
        layout.addWidget(self.repeat_combo)

        self.update_style()

    def update_style(self):
        """勾选后文字变灰并加删除线"""
        font = self.text_edit.font()
        font.setStrikeOut(self.checkbox.isChecked())
        self.text_edit.setFont(font)

        if self.checkbox.isChecked():
            self.text_edit.setStyleSheet("color: gray;")
        else:
            self.text_edit.setStyleSheet("color: black;")

    def trigger_save(self):
        """调用主窗口的保存函数"""
        if self.save_callback:
            self.save_callback()

    def check_reminder(self, tray_icon: QSystemTrayIcon):
        if self.checkbox.isChecked():
            return
        current_time = QDateTime.currentDateTime()
        remind_time = QDateTime(self.date_edit.date(), self.time_edit.time())   # ✅ 修复
        repeat = self.repeat_combo.currentText()
        if current_time >= remind_time and not self.notified:
            tray_icon.showMessage(
                "待办提醒",
                f"{self.text_edit.text()} 时间到了！",
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )
            self.notified = True
            if repeat == "每天":
                self.date_edit.setDate(self.date_edit.date().addDays(1))
                self.notified = False
            elif repeat == "每周":
                self.date_edit.setDate(self.date_edit.date().addDays(7))
                self.notified = False

    def to_dict(self):
        date = self.date_edit.date # QDate
        time = self.time_edit.time # QTime
        remind_time = QDateTime(date, time)
        return {
            "text": self.text_edit.text(),
            "remind_time": remind_time.toString("yyyy-MM-dd HH:mm:ss"),
            "repeat": self.repeat_combo.currentText(),
            "done": self.checkbox.isChecked()
        }
