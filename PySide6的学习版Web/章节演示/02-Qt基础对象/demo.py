"""原书 2.4.6：单击按钮后随机变换窗口背景颜色。"""

from random import choice

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QPushButton, QWidget


colorList = [
    QColor(15, 165, 80),
    QColor(200, 0, 12),
    QColor(5, 100, 60),
    QColor(13, 13, 80),
    QColor(20, 189, 255),
    QColor(10, 10, 0),
    QColor(120, 50, 95),
    QColor(58, 0, 0),
    QColor(100, 105, 16),
    QColor(0, 0, 200),
    QColor(199, 20, 150),
    QColor(40, 50, 88),
    QColor(118, 10, 0),
    QColor(55, 160, 28),
    QColor(0, 240, 17),
    QColor(91, 145, 28),
    QColor(33, 36, 125),
    QColor(88, 135, 201),
    QColor(232, 18, 52),
    QColor(42, 218, 50),
    QColor(89, 10, 180),
]


class MyWindow(QWidget):
    setColor = Signal(QColor)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("随机更换背景色")
        self.resize(300, 200)

        self.btn = QPushButton("换颜色", self)
        self.btn.move(15, 15)
        self.btn.clicked.connect(self.onClicked)
        self.setColor.connect(self.onColorPicked)

    def onClicked(self):
        selColor = choice(colorList)
        self.setColor.emit(selColor)

    def onColorPicked(self, color):
        palette = QPalette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec()
