# 可运行补全：网页 2.3.2 没有给出导入语句，以下导入为独立运行而补充。
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MyWindow(QWidget):
    # 构造函数
    def __init__(self):
        super().__init__(None)
        # 初始化可视化元素
        self.initUI()
        # 窗口标题
        self.setWindowTitle("发送键盘事件")

    def initUI(self):
        self.btnSelAll = QPushButton("全选")
        self.btnDelete = QPushButton("删除")
        self.btnBackspace = QPushButton("退格")
        self.btnMoveLeft = QPushButton("<-")
        self.btnMoveRight = QPushButton("->")
        self.text = QTextEdit()

        self.grid = QGridLayout(self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.btnSelAll)
        self.vbox.addWidget(self.btnDelete)
        self.vbox.addWidget(self.btnBackspace)
        self.vbox.addWidget(self.btnMoveLeft)
        self.vbox.addWidget(self.btnMoveRight)

        self.grid.addLayout(self.vbox, 0, 0)
        self.grid.addItem(QSpacerItem(15, 0), 0, 1)
        self.grid.addWidget(self.text, 0, 2)

        # 连接信号和槽
        self.btnSelAll.clicked.connect(self.onSelAll)
        self.btnDelete.clicked.connect(self.onDel)
        self.btnBackspace.clicked.connect(self.onBackSpace)
        self.btnMoveLeft.clicked.connect(self.onMoveLeft)
        self.btnMoveRight.clicked.connect(self.onMoveRight)

    def onSelAll(self):
        # Ctrl + A
        key = Qt.Key_A
        modf = Qt.ControlModifier
        # 发送键盘按下事件
        keyEvt = QKeyEvent(QKeyEvent.KeyPress, key, modf)
        QApplication.sendEvent(self.text, keyEvt)
        # 发送键盘释放事件
        keyEvt = QKeyEvent(QKeyEvent.KeyRelease, key, modf)
        QApplication.sendEvent(self.text, keyEvt)

    def onDel(self):
        # Delete
        key = Qt.Key_Delete
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyPress, key, Qt.NoModifier))
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyRelease, key, Qt.NoModifier))

    def onBackSpace(self):
        # BackSpace
        key = Qt.Key_Backspace
        modif = Qt.NoModifier
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyPress, key, modif))
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyRelease, key, modif))

    def onMoveLeft(self):
        # Left
        key = Qt.Key_Left
        mod = Qt.NoModifier
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyPress, key, mod))
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyRelease, key, mod))

    def onMoveRight(self):
        # Right
        key = Qt.Key_Right
        mod = Qt.NoModifier
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyPress, key, mod))
        QApplication.sendEvent(self.text, QKeyEvent(QKeyEvent.KeyRelease, key, mod))


# 可运行补全：网页 2.3.2 没有给出启动入口。
if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec()
