from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import QWidget, QApplication, QMessageBox

class MyElement(QWidget):
    # 构造函数
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        # 设置大小
        self.resize(180, 70)
        # 图示效果补充：网页原代码没有设置颜色，但图 2-2 显示为深色区域
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #333333;")

    # 重写 event 方法
    def event(self, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress:
            # 忽略此事件
            e.ignore()
            return True
        return super().event(e)

class MyWindow(QWidget):
    # 构造函数
    def __init__(self, parent=None) -> None:
        super().__init__(parent, Qt.Window)
        # 窗口标题
        self.setWindowTitle("示例程序")
        # 窗口大小
        self.resize(260, 200)

    # 重写 event 方法
    def event(self, e: QEvent) -> bool:
        # 如果是鼠标按下事件
        if e.type() == QEvent.MouseButtonPress:
            # 弹出消息框
            QMessageBox.information(self, "提示", "父窗口接收到鼠标事件", QMessageBox.Ok)
            # 已处理，返回 True
            return True
        return super().event(e)

if __name__ == "__main__":
    app = QApplication()
    # 实例化 MyWindow 类
    win = MyWindow()
    # 实例化 MyElement 类，它的父级对象是 win
    elm = MyElement(win)
    # 调整可视化对象在窗口上的位置
    elm.move(36, 30)
    # 显示窗口
    win.show()
    app.exec()
