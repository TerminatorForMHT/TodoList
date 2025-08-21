import datetime
import json
import os
import sys

from PyQt6.QtCore import Qt, QTimer, QPoint, QDateTime
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QListWidget, QSystemTrayIcon,
    QListWidgetItem, QApplication
)
from qfluentwidgets import (
    ListWidget, RoundMenu, FluentIcon, Action, isDarkTheme, ToolButton, MessageBox, SubtitleLabel
)
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from qfluentwidgets.window.fluent_window import FluentTitleBar

from config import IMG_PATH, DATA_FILE
from views.AddTaskBox import AddTaskBox
from views.TodoItemWidget import TodoItemWidget


class MainWindow(BackgroundAnimationWidget, FramelessWindow):
    """ Fluent window with ToDo list """

    def __init__(self, parent=None):
        self._isMicaEnabled = False
        self._lightBackgroundColor = QColor(240, 244, 249)
        self._darkBackgroundColor = QColor(32, 32, 32)
        self._isMaximizedFake = False
        self._normalGeometry = None

        super().__init__(parent=parent)

        self.resize(800, 600)

        # 顶层布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 40, 10, 10)

        # 开启 Mica
        self.setMicaEffectEnabled(True)

        # macOS 兼容
        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)

        # 标题栏
        self.setTitleBar(FluentTitleBar(self))
        self.titleBar.raise_()
        self.titleBar.setTitle('Fluent ToDo List')
        self.titleBar.setIcon(str(IMG_PATH / 'todo.svg'))
        self.titleBar.setContentsMargins(15, 0, 0, 0)
        self.setWindowIcon(QIcon(str(IMG_PATH / 'todo.ico')))

        # 绑定伪最大化（按钮）
        self.titleBar.maxBtn.clicked.disconnect()
        self.titleBar.maxBtn.clicked.connect(self.toggle_maximize)

        # 绑定伪最大化（双击标题栏）
        self.titleBar.mouseDoubleClickEvent = self._titlebar_double_click

        # 顶部按钮布局
        button_layout = QHBoxLayout()

        date_str = datetime.datetime.now().strftime("%Y年%m月%d日")
        time_label = SubtitleLabel()
        time_label.setText(date_str)

        add_button = ToolButton(FluentIcon.ADD)
        add_button.clicked.connect(self.add_task_dialog)

        button_layout.addWidget(time_label)
        button_layout.addStretch(1)
        button_layout.addWidget(add_button)
        button_layout.setContentsMargins(10, 10, 0, 0)

        # 任务列表
        self.task_list = ListWidget()
        self.task_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)

        # 添加到主布局
        self.main_layout.addLayout(button_layout)
        self.main_layout.addWidget(self.task_list)

        # 托盘图标
        self.tray_icon = QSystemTrayIcon(QIcon(str(IMG_PATH / "todo.svg")), self)
        self.tray_icon.setToolTip("Todo List 正在后台运行")
        self.tray_icon.setVisible(True)

        tray_menu = RoundMenu()
        tray_menu.addAction(Action('打开', triggered=self.show_window))
        tray_menu.addAction(Action('退出', triggered=self.quit_app))
        self.tray_icon.setContextMenu(tray_menu)

        # 定时器检查提醒
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60 * 1000)

        # 加载任务数据
        self.load_tasks()

    # ========== Mica 相关 ==========
    def isMicaEffectEnabled(self):
        return self._isMicaEnabled

    def setMicaEffectEnabled(self, isEnabled: bool):
        if sys.platform != 'win32' or sys.getwindowsversion().build < 22000:
            return

        self._isMicaEnabled = isEnabled
        if isEnabled:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        else:
            self.windowEffect.removeBackgroundEffect(self.winId())

    def _apply_mica(self):
        if self._isMicaEnabled:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

    # ✅ 伪造最大化（带恢复）
    def toggle_maximize(self):
        screen = self.screen().availableGeometry()
        if self._isMaximizedFake:
            # 还原
            if self._normalGeometry:
                self.setGeometry(self._normalGeometry)
            else:
                self.showNormal()
            self._isMaximizedFake = False
        else:
            # 保存原始位置和大小
            self._normalGeometry = self.geometry()
            # 模拟最大化（留 1px 边距，避免 Mica 失效）
            self.setGeometry(screen.adjusted(1, 1, -1, -1))
            self._isMaximizedFake = True

        self._apply_mica()

    def _titlebar_double_click(self, event):
        """双击标题栏触发伪最大化"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()

    # ========== 任务相关 ==========
    def add_task_dialog(self):
        dialog = AddTaskBox(self)
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

        menu = RoundMenu()
        delete_action = menu.addAction(Action(FluentIcon.DELETE, "删除选中任务"))
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

    # ========== 窗口事件 ==========
    def closeEvent(self, event):
        self.save_tasks()
        w = MessageBox("最小化到托盘", "程序会继续在后台运行，是否最小化到托盘", self)
        w.yesButton.setText('确认')
        w.cancelButton.setText('取消')

        if w.exec():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("Todo List", "程序已最小化到托盘",
                                       QSystemTrayIcon.MessageIcon.Information, 3000)
        else:
            event.accept()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        self.save_tasks()
        QApplication.quit()

    def save_tasks(self):
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget:
                tasks.append(widget.to_dict())
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            for task in tasks:
                dt = QDateTime.fromString(task["remind_time"], "yyyy-MM-dd HH:mm:ss")
                if not dt.isValid():
                    dt = QDateTime.currentDateTime()
                self.add_task(task["text"], dt, task.get("repeat", "不重复"), task.get("done", False))
        except Exception as e:
            print("加载任务失败:", e)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_mica()

    def changeEvent(self, event):
        super().changeEvent(event)
        self._apply_mica()
