task_style_sheet = """
QListWidget {
    background: transparent;
    border: none;
}
QListWidget::item {
    border-bottom: 1px solid rgba(0, 0, 0, 0.15);  /* 表格线，可调整透明度 */
}
QListWidget::item:selected {
    background: rgba(0, 120, 215, 0.2);  /* 选中高亮 */
}
"""
