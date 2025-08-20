import sys, json, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QCheckBox,
    QLabel, QDateTimeEdit, QComboBox, QDialog, QLineEdit,
    QDialogButtonBox, QMenu, QSystemTrayIcon, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime, QPoint, QTimer
from PyQt6.QtGui import QIcon


DATA_FILE = "tasks.json"


class TodoItemWidget(QWidget):
    """每一行的待办事项控件"""
    def __init__(self, text, remind_time, repeat, done=False, parent=None, save_callback=None):
        super().__init__(parent)

        self.notified = False
        self.save_callback = save_callback  # 传入保存函数

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # 完成状态
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.stateChanged.connect(self.update_style)
        self.checkbox.stateChanged.connect(self.trigger_save)

        # 任务文字（可编辑）
        self.text_edit = QLineEdit(text)
        self.text_edit.textChanged.connect(self.trigger_save)

        # 提醒时间
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setDateTime(remind_time)
        self.datetime_edit.dateTimeChanged.connect(self.trigger_save)

        # 重复周期
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["不重复", "每天", "每周"])
        self.repeat_combo.setCurrentText(repeat)
        self.repeat_combo.currentTextChanged.connect(self.trigger_save)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_edit, stretch=1)
        layout.addWidget(QLabel("提醒:"))
        layout.addWidget(self.datetime_edit)
        layout.addWidget(QLabel("重复:"))
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
        remind_time = self.datetime_edit.dateTime()
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
                self.datetime_edit.setDateTime(remind_time.addDays(1))
                self.notified = False
            elif repeat == "每周":
                self.datetime_edit.setDateTime(remind_time.addDays(7))
                self.notified = False

    def to_dict(self):
        return {
            "text": self.text_edit.text(),
            "remind_time": self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm"),
            "repeat": self.repeat_combo.currentText(),
            "done": self.checkbox.isChecked()
        }


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增待办事项")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("任务内容...")
        layout.addWidget(QLabel("任务:"))
        layout.addWidget(self.input_field)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(QLabel("提醒时间:"))
        layout.addWidget(self.datetime_edit)

        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["不重复", "每天", "每周"])
        layout.addWidget(QLabel("重复周期:"))
        layout.addWidget(self.repeat_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.input_field.text().strip(),
            self.datetime_edit.dateTime(),
            self.repeat_combo.currentText()
        )


class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")
        self.setGeometry(400, 200, 700, 400)

        layout = QVBoxLayout()

        # 按钮区
        button_layout = QHBoxLayout()
        add_button = QPushButton("新增任务")
        add_button.clicked.connect(self.add_task_dialog)
        button_layout.addWidget(add_button)

        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)

        layout.addLayout(button_layout)
        layout.addWidget(self.task_list)
        self.setLayout(layout)

        # 系统托盘
        self.tray_icon = QSystemTrayIcon(QIcon(), self)
        self.tray_icon.setToolTip("Todo List 正在后台运行")
        self.tray_icon.setVisible(True)

        tray_menu = QMenu()
        open_action = tray_menu.addAction("打开")
        quit_action = tray_menu.addAction("退出")
        open_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.quit_app)
        self.tray_icon.setContextMenu(tray_menu)

        # 定时器检查提醒
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60 * 1000)

        # 加载任务数据
        self.load_tasks()

    def add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            text, remind_time, repeat = dialog.get_data()
            if text:
                self.add_task(text, remind_time, repeat, done=False)
                self.save_tasks()

    def add_task(self, text, remind_time, repeat, done=False):
        item = QListWidgetItem(self.task_list)
        widget = TodoItemWidget(text, remind_time, repeat, done, save_callback=self.save_tasks)
        item.setSizeHint(widget.sizeHint())
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

    def show_context_menu(self, pos: QPoint):
        item = self.task_list.itemAt(pos)
        if item is None and not self.task_list.selectedItems():
            return
        menu = QMenu(self)
        delete_action = menu.addAction("删除选中任务")
        action = menu.exec(self.task_list.mapToGlobal(pos))
        if action == delete_action:
            self.delete_selected()

    def delete_selected(self):
        for item in self.task_list.selectedItems():
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
        self.save_tasks()

    def check_reminders(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget:
                widget.check_reminder(self.tray_icon)

    def closeEvent(self, event):
        """最小化到托盘并保存任务"""
        self.save_tasks()
        reply = QMessageBox.question(
            self, "最小化到托盘",
            "程序会继续在后台运行，是否最小化到托盘？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("Todo List", "程序已最小化到托盘", QSystemTrayIcon.MessageIcon.Information, 3000)
        else:
            event.accept()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        self.save_tasks()
        QApplication.quit()

    def save_tasks(self):
        """保存所有任务到 JSON 文件"""
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget:
                tasks.append(widget.to_dict())
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        """加载任务数据"""
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            for task in tasks:
                dt = QDateTime.fromString(task["remind_time"], "yyyy-MM-dd HH:mm")
                if not dt.isValid():
                    dt = QDateTime.currentDateTime()
                self.add_task(task["text"], dt, task.get("repeat", "不重复"), task.get("done", False))
        except Exception as e:
            print("加载任务失败:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec())
