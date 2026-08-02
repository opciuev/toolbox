from PySide6.QtCore import *
from PySide6.QtGui import *

class MyUI(QWindow):
    # 构造函数
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标题
        self.setTitle("示例程序")
        # 设置窗口大小
        self.resize(280, 245)

    # 处理事件
    def event(self, e: QEvent) -> bool:
        # 判断是否为键盘按下事件
        if e.type() == QEvent.KeyPress:
            keyevent: QKeyEvent = e
            if keyevent.key() == Qt.Key_Left:
                print("你按下了【向左】键")
            if keyevent.key() == Qt.Key_Right:
                print("你按下了【向右】键")
            if keyevent.key() == Qt.Key_Up:
                print("你按下了【向上】键")
            if keyevent.key() == Qt.Key_Down:
                print("你按下了【向下】键")
            # 已处理过，返回 True
            return True
        # 其他事件交由基类去处理
        return super().event(e)

if __name__ == "__main__":
    app = QGuiApplication()
    obj = MyUI()
    # 显示窗口
    obj.show()
    # 开始消息循环
    app.exec()
