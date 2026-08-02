# 可运行补全：网页 2.3.4 没有给出导入语句，以下导入为独立运行而补充。
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget


class EventFilter1(QObject):
    # 构造函数
    def __init__(self, parent=None):
        super().__init__(parent)

    # 重写事件过滤方法
    def eventFilter(self, watched: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress:
            print("事件过滤器 - 1")
        return super().eventFilter(watched, e)


class EventFilter2(QObject):
    # 构造函数
    def __init__(self, parent=None):
        super().__init__(parent)

    # 重写事件过滤方法
    def eventFilter(self, watched: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress:
            print("事件过滤器 - 2")
        return super().eventFilter(watched, e)


class EventFilter3(QObject):
    # 构造函数
    def __init__(self, parent=None):
        super().__init__(parent)

    # 重写事件过滤方法
    def eventFilter(self, watched: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress:
            print("事件过滤器 - 3")
        return super().eventFilter(watched, e)


class MyWindow(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.Window)
        # 窗口标题
        self.setWindowTitle("Demo App")
        # 窗口大小
        self.resize(240, 70)
        # 窗口位置
        self.move(548, 438)
        # 实例化按钮部件
        self.btn = QPushButton("请单击这里", self)
        # 设置按钮的位置
        self.btn.move(20, 20)
        # 实例化三个事件过滤器
        self.evtFilter1 = EventFilter1(self)
        self.evtFilter2 = EventFilter2(self)
        self.evtFilter3 = EventFilter3(self)
        # 注册事件过滤器
        self.btn.installEventFilter(self.evtFilter1)
        self.btn.installEventFilter(self.evtFilter2)
        self.btn.installEventFilter(self.evtFilter3)


# 可运行补全：网页没有给出本示例的启动入口。
if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec()
