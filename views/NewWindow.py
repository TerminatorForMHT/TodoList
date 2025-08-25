import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets.window.fluent_window import FluentWindowBase


class MainWindow(FluentWindowBase):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # # 创建子界面，实际使用时将 Widget 换成自己的子界面
        # self.homeInterface = Widget('Home Interface', self)
        # self.musicInterface = Widget('Music Interface', self)
        # self.videoInterface = Widget('Video Interface', self)
        # self.settingInterface = Widget('Setting Interface', self)
        # self.albumInterface = Widget('Album Interface', self)
        # self.albumInterface1 = Widget('Album Interface 1', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        # self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        # self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        # self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')
        #
        # self.navigationInterface.addSeparator()
        #
        # self.addSubInterface(self.albumInterface, FIF.ALBUM, 'Albums', NavigationItemPosition.SCROLL)
        # self.addSubInterface(self.albumInterface1, FIF.ALBUM, 'Album 1', parent=self.albumInterface)
        #
        # self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        pass

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
