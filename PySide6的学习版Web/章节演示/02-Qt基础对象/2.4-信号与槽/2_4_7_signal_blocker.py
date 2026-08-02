"""原书 2.4.7：使用 QSignalBlocker 暂停定时器信号。"""

import PySide6.QtCore as core
import PySide6.QtGui as gui
import PySide6.QtWidgets as widgets


class AppWindow(widgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.resize(265, 98)

        self.btn = widgets.QPushButton("暂停 10 秒", self)
        self.btn.move(20, 12)
        self.btn.clicked.connect(self.onBtnClicked)

        self.lb = widgets.QLabel("示例文本", self)
        self.lb.setFont(gui.QFont("仿宋", 15, gui.QFont.Bold))
        self.lb.move(20, 50)

        self.timer = core.QTimer(self)
        self.timer.timeout.connect(self.onTimeout)
        self.timer.start(1000)

    def onTimeout(self):
        self.lb.setVisible(not self.lb.isVisible())

    def onBtnClicked(self):
        with core.QSignalBlocker(self.timer):
            event_loop = core.QEventLoop(self)
            core.QTimer.singleShot(10 * 1000, event_loop.quit)
            event_loop.exec()


if __name__ == "__main__":
    app = widgets.QApplication()
    window = AppWindow()
    window.show()
    app.exec()
